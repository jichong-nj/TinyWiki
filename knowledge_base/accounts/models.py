from django.contrib.auth.models import AbstractUser
from django.db import models
from documents.models import KnowledgeBase, Directory


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('superuser', '超级管理员'),
            ('knowledge_admin', '知识管理员'),
            ('knowledge_user', '知识使用者'),
        ],
        default='knowledge_user'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class UserPermission(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assigned_permissions'
    )
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='assigned_permissions',
        null=True,
        blank=True
    )
    directory = models.ForeignKey(
        Directory,
        on_delete=models.CASCADE,
        related_name='assigned_permissions',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'knowledge_base', 'directory']
        verbose_name = '用户权限'
        verbose_name_plural = '用户权限'

    def __str__(self):
        return f"{self.user.username} - {self.knowledge_base or self.directory}"
