from django.db import models
import hashlib


class FileStorage(models.Model):
    """文件存储模型"""
    STORAGE_TYPES = [
        ('original', '原始文件'),
        ('converted', '转换文件'),
        ('attachment', '附件'),
        ('chunk', '文档片段'),
        ('embedding', '向量嵌入'),
        ('thumbnail', '缩略图'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    md5_hash = models.CharField(max_length=32, unique=True, db_index=True, verbose_name='MD5哈希')
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    file_type = models.CharField(max_length=50, verbose_name='文件类型')
    mime_type = models.CharField(max_length=100, blank=True, verbose_name='MIME类型')
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES, verbose_name='存储类型')
    relative_path = models.CharField(max_length=500, verbose_name='相对路径')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 关联文档（可选）
    document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='files', 
                               verbose_name='关联文档')
    
    class Meta:
        db_table = 'file_storage'
        verbose_name = '文件存储'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.file_name} ({self.md5_hash})"
    
    @property
    def full_path(self):
        """获取完整文件路径"""
        from django.conf import settings
        return settings.STORAGE_ROOT / self.relative_path
    
    @property
    def file_url(self):
        """获取文件访问URL"""
        from django.conf import settings
        return f"/storage/{self.relative_path}"
    
    @classmethod
    def get_md5(cls, file_obj):
        """计算文件MD5"""
        md5 = hashlib.md5()
        if hasattr(file_obj, 'chunks'):
            # Django File对象
            for chunk in file_obj.chunks():
                md5.update(chunk)
        else:
            # BytesIO对象
            file_obj.seek(0)
            for chunk in iter(lambda: file_obj.read(4096), b''):
                md5.update(chunk)
            file_obj.seek(0)
        return md5.hexdigest()
    
    @classmethod
    def get_md5_from_path(cls, file_path):
        """从文件路径计算MD5"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()
    
    @classmethod
    def get_storage_path(cls, md5_hash, sub_dir=''):
        """根据MD5获取存储路径"""
        level1 = md5_hash[:2]
        level2 = md5_hash[2:4]
        path_parts = [level1, level2, md5_hash]
        if sub_dir:
            path_parts.insert(0, sub_dir)
        return '/'.join(path_parts)


class FileAttachment(models.Model):
    """文档附件模型"""
    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, 
                               related_name='attachments', verbose_name='所属文档')
    file_storage = models.ForeignKey('FileStorage', on_delete=models.CASCADE, 
                                    verbose_name='存储文件')
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    description = models.TextField(blank=True, verbose_name='描述')
    position = models.IntegerField(default=0, verbose_name='排序位置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'file_attachment'
        verbose_name = '文档附件'
        verbose_name_plural = verbose_name
        ordering = ['position', 'created_at']
    
    def __str__(self):
        return f"{self.original_name} - {self.document.title}"


class DocumentConversion(models.Model):
    """文档转换记录模型"""
    STATUS_CHOICES = [
        ('pending', '待转换'),
        ('converting', '转换中'),
        ('success', '转换成功'),
        ('failed', '转换失败'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    original_file = models.ForeignKey('FileStorage', on_delete=models.CASCADE, 
                                     related_name='conversions', verbose_name='原始文件')
    converted_file = models.ForeignKey('FileStorage', on_delete=models.SET_NULL, 
                                       null=True, blank=True, 
                                       related_name='source_conversions', 
                                       verbose_name='转换后文件')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='pending', verbose_name='转换状态')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    conversion_info = models.JSONField(default=dict, verbose_name='转换信息')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'document_conversion'
        verbose_name = '文档转换记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_file.file_name} - {self.status}"
