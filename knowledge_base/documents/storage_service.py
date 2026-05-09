import os
import hashlib
import json
import uuid
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from .storage_models import FileStorage


class StorageService:
    """文件存储服务"""
    
    @classmethod
    def save_file(cls, file_obj, storage_type='original', document=None, 
                 original_name=None, content=None):
        """
        保存文件
        
        Args:
            file_obj: 文件对象 (django上传的File对象)
            storage_type: 存储类型
            document: 关联文档
            original_name: 原始文件名
            content: 文件内容 (可选，用于直接保存文本)
            
        Returns:
            FileStorage 对象
        """
        # 计算MD5
        if content is not None:
            md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        else:
            md5_hash = FileStorage.get_md5(file_obj)
        
        # 检查是否已存在
        existing = FileStorage.objects.filter(md5_hash=md5_hash, 
                                            storage_type=storage_type).first()
        if existing:
            # 如果传入了新的文档，需要更新关联
            if document and existing.document_id != document.id:
                existing.document = document
                existing.save()
                # 更新 info.json
                cls._save_file_info(existing, Path(existing.full_path).parent)
            return existing
        
        # 获取存储路径
        relative_path = FileStorage.get_storage_path(md5_hash, storage_type)
        full_path = settings.STORAGE_ROOT / relative_path
        
        # 创建目录
        full_path.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_name = original_name or file_obj.name if file_obj else f"{md5_hash}.txt"
        file_path = full_path / file_name
        
        if content is not None:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_size = len(content.encode('utf-8'))
            file_type = file_name.split('.')[-1].lower() if '.' in file_name else 'txt'
            mime_type = 'text/plain'
        else:
            with open(file_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            file_size = file_obj.size
            file_type = file_name.split('.')[-1].lower() if '.' in file_name else ''
            mime_type = file_obj.content_type if hasattr(file_obj, 'content_type') else ''
        
        # 保存元信息
        file_storage = FileStorage.objects.create(
            md5_hash=md5_hash,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            storage_type=storage_type,
            relative_path=f"{relative_path}/{file_name}",
            document=document
        )
        
        # 保存info.json
        cls._save_file_info(file_storage, file_path.parent)
        
        return file_storage
    
    @classmethod
    def save_file_from_path(cls, source_path, storage_type='original', 
                          document=None, original_name=None):
        """
        从文件路径保存文件
        
        Args:
            source_path: 源文件路径
            storage_type: 存储类型
            document: 关联文档
            original_name: 原始文件名
            
        Returns:
            FileStorage 对象
        """
        # 计算MD5
        md5_hash = FileStorage.get_md5_from_path(source_path)
        
        # 检查是否已存在
        existing = FileStorage.objects.filter(md5_hash=md5_hash, 
                                            storage_type=storage_type).first()
        if existing:
            # 如果传入了新的文档，需要更新关联
            if document and existing.document_id != document.id:
                existing.document = document
                existing.save()
                # 更新 info.json
                cls._save_file_info(existing, Path(existing.full_path).parent)
            return existing
        
        # 获取存储路径
        relative_path = FileStorage.get_storage_path(md5_hash, storage_type)
        full_path = settings.STORAGE_ROOT / relative_path
        
        # 创建目录
        full_path.mkdir(parents=True, exist_ok=True)
        
        # 读取源文件并保存
        file_name = original_name or Path(source_path).name
        file_path = full_path / file_name
        
        import shutil
        shutil.copy2(source_path, file_path)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_type = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        # 保存元信息
        file_storage = FileStorage.objects.create(
            md5_hash=md5_hash,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            mime_type='',
            storage_type=storage_type,
            relative_path=f"{relative_path}/{file_name}",
            document=document
        )
        
        # 保存info.json
        cls._save_file_info(file_storage, file_path.parent)
        
        return file_storage
    
    @classmethod
    def _save_file_info(cls, file_storage, dir_path):
        """保存文件元信息"""
        info = {
            'md5': file_storage.md5_hash,
            'file_name': file_storage.file_name,
            'file_size': file_storage.file_size,
            'file_type': file_storage.file_type,
            'created_at': file_storage.created_at.isoformat(),
            'document_id': file_storage.document_id,
        }
        info_path = dir_path / 'info.json'
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def get_file(cls, md5_hash, storage_type='original'):
        """获取文件"""
        file_storage = FileStorage.objects.filter(md5_hash=md5_hash, 
                                                storage_type=storage_type).first()
        if not file_storage:
            return None
        return file_storage
    
    @classmethod
    def get_file_by_id(cls, file_id):
        """通过ID获取文件"""
        try:
            return FileStorage.objects.get(id=file_id)
        except FileStorage.DoesNotExist:
            return None
    
    @classmethod
    def delete_file(cls, md5_hash, storage_type='original'):
        """删除文件"""
        file_storage = FileStorage.objects.filter(md5_hash=md5_hash, 
                                                storage_type=storage_type).first()
        if file_storage:
            try:
                # 删除物理文件
                file_path = file_storage.full_path
                if file_path.exists():
                    file_path.unlink()
                
                # 删除info.json
                info_path = file_path.parent / 'info.json'
                if info_path.exists():
                    info_path.unlink()
                
                # 尝试删除空目录
                try:
                    file_path.parent.rmdir()
                except:
                    pass
                
                # 删除数据库记录
                file_storage.delete()
                return True
            except Exception as e:
                print(f"删除文件失败: {e}")
                return False
        return False
