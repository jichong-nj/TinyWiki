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
    PermissionDetailView
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
]