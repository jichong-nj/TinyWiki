import os
import json
import tempfile
from pathlib import Path
from django.utils import timezone
from django.conf import settings
from .storage_models import FileStorage, FileAttachment, DocumentConversion
from .storage_service import StorageService


class DocumentConverter:
    """文档转换器"""
    
    SUPPORTED_TYPES = ['docx', 'doc', 'md', 'txt']
    
    @classmethod
    def convert(cls, file_storage_id):
        """
        同步转换文档
        
        Args:
            file_storage_id: FileStorage对象的ID
            
        Returns:
            dict: 转换结果
        """
        try:
            file_storage = StorageService.get_file_by_id(file_storage_id)
            if not file_storage:
                return {'success': False, 'error': '文件不存在'}
            
            # 创建转换记录
            conversion = DocumentConversion.objects.create(
                original_file=file_storage,
                status='converting',
                started_at=timezone.now()
            )
            
            # 根据文件类型选择转换器
            file_type = file_storage.file_type.lower()
            
            if file_type in ['docx']:
                result = cls._convert_docx(file_storage, conversion)
            elif file_type in ['md', 'txt']:
                result = cls._convert_text(file_storage, conversion)
            else:
                result = {'success': False, 'error': f'不支持的文件类型: {file_type}'}
            
            # 更新转换状态
            if result['success']:
                conversion.status = 'success'
                conversion.converted_file = result.get('converted_file')
                conversion.conversion_info = result.get('info', {})
            else:
                conversion.status = 'failed'
                conversion.error_message = result.get('error', '未知错误')
            
            conversion.completed_at = timezone.now()
            conversion.save()
            
            return result
            
        except Exception as e:
            import traceback
            error_msg = f"转换失败: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            
            try:
                # 尝试更新转换记录
                conversion = DocumentConversion.objects.filter(original_file_id=file_storage_id).first()
                if conversion:
                    conversion.status = 'failed'
                    conversion.error_message = error_msg
                    conversion.completed_at = timezone.now()
                    conversion.save()
            except:
                pass
            
            return {'success': False, 'error': error_msg}
    
    @classmethod
    def convert_async(cls, file_storage_id):
        """
        异步转换文档（这里简化为同步调用，实际项目中可以使用Celery）
        
        Args:
            file_storage_id: FileStorage对象的ID
        """
        # 简化实现，直接同步调用
        return cls.convert(file_storage_id)
    
    @classmethod
    def _convert_docx(cls, file_storage, conversion):
        """
        转换Word文档
        
        Args:
            file_storage: FileStorage对象
            conversion: DocumentConversion对象
            
        Returns:
            dict: 转换结果
        """
        try:
            # 尝试使用python-docx
            import docx
        except ImportError:
            return cls._convert_docx_simple(file_storage, conversion)
        
        try:
            document = docx.Document(file_storage.full_path)
            
            # 存储提取的图片
            attachments = []
            image_map = {}
            
            # 提取图片
            for rel in document.part.rels.values():
                if 'image' in rel.target_ref:
                    image_data = rel.target_part.blob
                    
                    # 保存图片为附件
                    image_name = f"image_{len(attachments)+1}.{rel.target_ref.split('.')[-1]}"
                    
                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{rel.target_ref.split('.')[-1]}") as f:
                        f.write(image_data)
                        temp_path = f.name
                    
                    try:
                        # 保存到附件库
                        image_file = StorageService.save_file_from_path(
                            source_path=temp_path,
                            storage_type='attachment',
                            document=file_storage.document,
                            original_name=image_name
                        )
                        
                        # 创建附件关联
                        if file_storage.document:
                            attachment = FileAttachment.objects.create(
                                document=file_storage.document,
                                file_storage=image_file,
                                original_name=image_name,
                                description=f"从{file_storage.file_name}中提取的图片",
                                position=len(attachments)
                            )
                        
                        attachments.append(image_file)
                        image_map[rel.rId] = image_file.file_url
                    finally:
                        # 删除临时文件
                        os.unlink(temp_path)
            
            # 转换内容为Markdown
            markdown_content = []
            
            # 处理段落（包括段落内的图片）
            for paragraph in document.paragraphs:
                # 检查段落中是否有图片并插入
                for run in paragraph.runs:
                    for inline in run.element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'):
                        for blip in inline.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
                            rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                            if rId and rId in image_map:
                                # 找到对应的图片文件
                                img_file = None
                                for idx, af in enumerate(attachments):
                                    if af.file_url == image_map[rId]:
                                        img_file = af
                                        break
                                if img_file:
                                    markdown_content.append(f"![{img_file.file_name}]({image_map[rId]})\n")
                
                # 不管有没有图片，都处理文本
                if paragraph.style.name.startswith('Heading 1'):
                    markdown_content.append(f"# {paragraph.text}\n")
                elif paragraph.style.name.startswith('Heading 2'):
                    markdown_content.append(f"## {paragraph.text}\n")
                elif paragraph.style.name.startswith('Heading 3'):
                    markdown_content.append(f"### {paragraph.text}\n")
                elif paragraph.text.strip():
                    markdown_content.append(f"{paragraph.text}\n")
                else:
                    markdown_content.append("\n")
            
            # 处理表格
            for table in document.tables:
                markdown_content.append("\n")
                for i, row in enumerate(table.rows):
                    cells = [cell.text.strip() for cell in row.cells]
                    markdown_content.append(f"| {' | '.join(cells)} |\n")
                    if i == 0:
                        markdown_content.append(f"| {' | '.join(['---'] * len(cells))} |\n")
            
            # 如果有图片但没有在段落中找到，就全部添加到最后
            if len(attachments) > 0 and not any('![' in item for item in markdown_content):
                markdown_content.append("\n---\n")
                markdown_content.append("## 提取的图片\n\n")
                for img_file in attachments:
                    markdown_content.append(f"![{img_file.file_name}]({img_file.file_url})\n\n")
            
            markdown_text = ''.join(markdown_content)
            
            # 保存转换后的Markdown
            converted_name = Path(file_storage.file_name).stem + '.md'
            converted_file = StorageService.save_file(
                file_obj=None,
                storage_type='converted',
                document=file_storage.document,
                original_name=converted_name,
                content=markdown_text
            )
            
            # 更新文档内容（如果有关联文档）
            if file_storage.document:
                file_storage.document.content = markdown_text
                file_storage.document.save()
            
            # 保存转换信息
            conversion_info = {
                'attachments_count': len(attachments),
                'image_map': {k: v for k, v in image_map.items()},
                'paragraphs_count': len(document.paragraphs),
                'tables_count': len(document.tables)
            }
            
            return {
                'success': True,
                'converted_file': converted_file,
                'info': conversion_info,
                'markdown': markdown_text
            }
            
        except Exception as e:
            import traceback
            return {'success': False, 'error': f'DOCX转换失败: {str(e)}\n{traceback.format_exc()}'}
    
    @classmethod
    def _convert_docx_simple(cls, file_storage, conversion):
        """
        简化的Word文档转换（当没有python-docx时使用）
        
        Args:
            file_storage: FileStorage对象
            conversion: DocumentConversion对象
            
        Returns:
            dict: 转换结果
        """
        try:
            # 读取原始文件内容
            content = f"# {Path(file_storage.file_name).stem}\n\n"
            content += f"此文件为Word文档，请安装python-docx库以获得更好的转换效果。\n\n"
            content += f"原始文件名: {file_storage.file_name}\n"
            content += f"文件大小: {file_storage.file_size} bytes\n"
            
            # 保存转换后的Markdown
            converted_name = Path(file_storage.file_name).stem + '.md'
            converted_file = StorageService.save_file(
                file_obj=None,
                storage_type='converted',
                document=file_storage.document,
                original_name=converted_name,
                content=content
            )
            
            # 更新文档内容（如果有关联文档）
            if file_storage.document:
                file_storage.document.content = content
                file_storage.document.save()
            
            conversion_info = {
                'method': 'simple',
                'warning': '未安装python-docx库，使用简化转换'
            }
            
            return {
                'success': True,
                'converted_file': converted_file,
                'info': conversion_info,
                'markdown': content
            }
            
        except Exception as e:
            return {'success': False, 'error': f'简化转换失败: {str(e)}'}
    
    @classmethod
    def _convert_text(cls, file_storage, conversion):
        """
        转换文本文件（Markdown或TXT）
        
        Args:
            file_storage: FileStorage对象
            conversion: DocumentConversion对象
            
        Returns:
            dict: 转换结果
        """
        try:
            # 直接读取文件内容
            with open(file_storage.full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果是txt文件，添加标题
            if file_storage.file_type.lower() == 'txt':
                title = Path(file_storage.file_name).stem
                content = f"# {title}\n\n{content}"
            
            # 保存转换后的Markdown（其实就是原样保存）
            converted_name = Path(file_storage.file_name).stem + '.md'
            converted_file = StorageService.save_file(
                file_obj=None,
                storage_type='converted',
                document=file_storage.document,
                original_name=converted_name,
                content=content
            )
            
            # 更新文档内容（如果有关联文档）
            if file_storage.document:
                file_storage.document.content = content
                file_storage.document.save()
            
            conversion_info = {
                'method': 'direct',
                'content_length': len(content)
            }
            
            return {
                'success': True,
                'converted_file': converted_file,
                'info': conversion_info,
                'markdown': content
            }
            
        except Exception as e:
            return {'success': False, 'error': f'文本转换失败: {str(e)}'}
