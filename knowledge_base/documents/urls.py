from django.urls import path
from .views import (
    KnowledgeBaseListView,
    KnowledgeBaseDetailView,
    DirectoryListView,
    DirectoryDetailView,
    FolderListView,
    FolderDetailView,
    DocumentListView,
    DocumentDetailView,
    DocumentVersionListView,
    DocumentPublishView,
    DocumentTreeView,
    DocumentSearchView,
    VectorSearchView,
    PermissionListView,
    PermissionDetailView,
    FileUploadView,
    FileUploadMultipleView,
    FileAccessView,
    FileInfoView,
    DocumentAttachmentListView,
    ConversionStatusView
)

urlpatterns = [
    path('knowledge-bases/', KnowledgeBaseListView.as_view(), name='knowledge-base-list'),
    path('knowledge-bases/<int:pk>/', KnowledgeBaseDetailView.as_view(), name='knowledge-base-detail'),
    path('knowledge-bases/<int:knowledge_base_id>/tree/', DocumentTreeView.as_view(), name='knowledge-base-tree'),
    
    path('directories/', DirectoryListView.as_view(), name='directory-list'),
    path('directories/<int:pk>/', DirectoryDetailView.as_view(), name='directory-detail'),
    
    path('folders/', FolderListView.as_view(), name='folder-list'),
    path('folders/<int:pk>/', FolderDetailView.as_view(), name='folder-detail'),
    
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/publish/', DocumentPublishView.as_view(), name='document-publish'),
    path('documents/<int:document_id>/versions/', DocumentVersionListView.as_view(), name='document-versions'),
    path('documents/search/', DocumentSearchView.as_view(), name='document-search'),
    path('documents/vector-search/', VectorSearchView.as_view(), name='vector-search'),
    
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', PermissionDetailView.as_view(), name='permission-detail'),
    
    # 文件上传和存储
    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/upload-multiple/', FileUploadMultipleView.as_view(), name='file-upload-multiple'),
    path('files/<str:md5_hash>/', FileAccessView.as_view(), name='file-access'),
    path('files/info/<int:file_id>/', FileInfoView.as_view(), name='file-info'),
    
    # 文档附件
    path('documents/<int:document_id>/attachments/', DocumentAttachmentListView.as_view(), name='document-attachments'),
    
    # 转换状态
    path('conversions/<int:conversion_id>/', ConversionStatusView.as_view(), name='conversion-status'),
]