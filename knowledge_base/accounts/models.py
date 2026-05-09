from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('super_admin', '超级管理员'),
            ('admin', '管理员'),
            ('member', '普通成员'),
        ],
        default='member'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
