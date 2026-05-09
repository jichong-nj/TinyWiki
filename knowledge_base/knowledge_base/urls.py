from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from documents.storage_models import FileStorage


def storage_file_view(request, md5_hash):
    """存储文件访问视图"""
    file_storage = get_object_or_404(FileStorage, md5_hash=md5_hash)
    file_path = file_storage.full_path
    return FileResponse(
        open(file_path, 'rb'),
        filename=file_storage.file_name,
        content_type=file_storage.mime_type or 'application/octet-stream'
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('api.urls')),
    path('api/', include('documents.urls')),
    path('storage/files/<str:md5_hash>/', storage_file_view, name='storage-file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)