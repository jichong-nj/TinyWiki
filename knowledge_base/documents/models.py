from django.db import models
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.db.models.signals import post_save, post_delete
from pgvector.django import VectorField


class KnowledgeBase(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Directory(models.Model):
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='directories'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.knowledge_base.name} / {self.name}"


class Folder(models.Model):
    directory = models.ForeignKey(
        Directory,
        on_delete=models.CASCADE,
        related_name='folders',
        blank=True,
        null=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            # 顶级文件夹（在 directory 下）：directory 和 name 必须唯一
            models.UniqueConstraint(
                fields=['directory', 'name'],
                name='unique_directory_name',
                condition=models.Q(parent__isnull=True)
            ),
            # 子文件夹（在 parent 下）：parent 和 name 必须唯一
            models.UniqueConstraint(
                fields=['parent', 'name'],
                name='unique_parent_name',
                condition=models.Q(parent__isnull=False)
            )
        ]


class Document(models.Model):
    directory = models.ForeignKey(
        Directory,
        on_delete=models.CASCADE,
        related_name='documents',
        blank=True,
        null=True
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        related_name='documents',
        blank=True,
        null=True
    )
    title = models.CharField(max_length=200)
    filename = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    search_vector = SearchVectorField(null=True, blank=True)
    publish_status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '未发布'),
            ('published', '已发布'),
        ],
        default='draft'
    )
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '未分析'),
            ('analyzing', '分析中'),
            ('completed', '已分析'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_current_version(self):
        latest_version = self.versions.order_by('-version_number').first()
        return latest_version.version_number if latest_version else 1
    
    class Meta:
        constraints = [
            # 顶级文档（在 directory 下）：directory 和 filename 必须唯一
            models.UniqueConstraint(
                fields=['directory', 'filename'],
                name='unique_directory_filename',
                condition=models.Q(folder__isnull=True)
            ),
            # 文档在 folder 下：folder 和 filename 必须唯一
            models.UniqueConstraint(
                fields=['folder', 'filename'],
                name='unique_folder_filename',
                condition=models.Q(folder__isnull=False)
            )
        ]


class DocumentVersion(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.IntegerField()
    content = models.TextField()
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_versions'
    )
    change_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
    
    class Meta:
        unique_together = ('document', 'version_number')


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    content = models.TextField()
    # 旧的 JSON 字段（保留用于兼容）
    embedding = models.TextField(null=True, blank=True)
    # 新的 pgvector 字段（默认 1024 维）
    embedding_vector = VectorField(dimensions=1024, null=True, blank=True)
    chunk_index = models.IntegerField()
    chunk_size = models.IntegerField()
    overlap_size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
    
    class Meta:
        ordering = ['chunk_index']


class Permission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    directory = models.ForeignKey(
        Directory,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', '目录管理员'),
            ('editor', '编辑者'),
            ('viewer', '查看者'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.directory.name} - {self.role}"
    
    class Meta:
        unique_together = ('user', 'directory')


# 导入存储相关模型
from .storage_models import FileStorage, FileAttachment, DocumentConversion

# 导入聊天相关模型
from .chat_models import ChatSession, ChatMessage