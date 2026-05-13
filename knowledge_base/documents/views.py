import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from django.db import models
from .models import KnowledgeBase, Directory, Folder, Document, DocumentVersion, Permission
from .serializers import (
    KnowledgeBaseSerializer,
    DirectorySerializer,
    FolderSerializer,
    DocumentSerializer,
    DocumentVersionSerializer,
    PermissionSerializer,
    PermissionCreateSerializer
)


class KnowledgeBaseListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bases = KnowledgeBase.objects.all()
        serializer = KnowledgeBaseSerializer(bases, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = KnowledgeBaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KnowledgeBaseDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            base = KnowledgeBase.objects.get(pk=pk)
            serializer = KnowledgeBaseSerializer(base)
            return Response(serializer.data)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': 'KnowledgeBase not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            base = KnowledgeBase.objects.get(pk=pk)
            serializer = KnowledgeBaseSerializer(base, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': 'KnowledgeBase not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            base = KnowledgeBase.objects.get(pk=pk)
            base.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': 'KnowledgeBase not found'}, status=status.HTTP_404_NOT_FOUND)


class DirectoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        knowledge_base_id = request.query_params.get('knowledge_base')
        if knowledge_base_id:
            directories = Directory.objects.filter(knowledge_base_id=knowledge_base_id)
        else:
            directories = Directory.objects.all()
        serializer = DirectorySerializer(directories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DirectorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            directory = Directory.objects.get(pk=pk)
            serializer = DirectorySerializer(directory)
            return Response(serializer.data)
        except Directory.DoesNotExist:
            return Response({'error': 'Directory not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            directory = Directory.objects.get(pk=pk)
            serializer = DirectorySerializer(directory, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Directory.DoesNotExist:
            return Response({'error': 'Directory not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            directory = Directory.objects.get(pk=pk)
            directory.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Directory.DoesNotExist:
            return Response({'error': 'Directory not found'}, status=status.HTTP_404_NOT_FOUND)


class FolderListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        directory_id = request.query_params.get('directory')
        parent_id = request.query_params.get('parent')
        
        print(f'FolderListView查询: directory={directory_id}, parent={parent_id}')
        
        folders = Folder.objects.all()
        
        # 处理parent参数
        if parent_id is not None:
            if parent_id == 'null' or parent_id == 'None' or parent_id == '':
                # 明确请求顶层文件夹（parent为空），需要过滤directory
                if directory_id:
                    folders = folders.filter(directory_id=directory_id)
                folders = folders.filter(parent__isnull=True)
            else:
                # 请求特定parent的子文件夹，不需要过滤directory（子文件夹可能没有directory）
                try:
                    parent_id_int = int(parent_id)
                    folders = folders.filter(parent_id=parent_id_int)
                except (ValueError, TypeError):
                    pass
        else:
            # 如果没有parent参数，默认只返回顶层文件夹，需要过滤directory
            if directory_id:
                folders = folders.filter(directory_id=directory_id)
            folders = folders.filter(parent__isnull=True)
        
        print(f'返回文件夹数量: {len(folders)}')
        for f in folders:
            print(f'  - 文件夹: {f.id} - {f.name}, parent: {f.parent_id}')
        
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FolderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            folder = Folder.objects.get(pk=pk)
            serializer = FolderSerializer(folder)
            return Response(serializer.data)
        except Folder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            folder = Folder.objects.get(pk=pk)
            serializer = FolderSerializer(folder, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Folder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            folder = Folder.objects.get(pk=pk)
            
            # 递归获取所有子文件夹
            def get_all_subfolders(folder_obj):
                subfolders = [folder_obj]
                for child in folder_obj.children.all():
                    subfolders.extend(get_all_subfolders(child))
                return subfolders
            
            all_folders = get_all_subfolders(folder)
            folder_ids = [f.id for f in all_folders]
            
            print(f'删除文件夹 {folder.name}，包含 {len(all_folders)} 个子文件夹，及其下的所有文档')
            
            # 删除所有关联的文档（包括子文件夹中的）
            documents = Document.objects.filter(folder_id__in=folder_ids)
            doc_count = documents.count()
            print(f'将删除 {doc_count} 个文档')
            
            # 删除文档
            documents.delete()
            
            # 删除文件夹（会级联删除子文件夹）
            folder.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Folder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        directory_id = request.query_params.get('directory')
        folder_id = request.query_params.get('folder')
        documents = Document.objects.all()
        if folder_id:
            documents = documents.filter(folder_id=folder_id)
        elif directory_id:
            documents = documents.filter(directory_id=directory_id, folder__isnull=True)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if 'file' in request.data:
            file = request.data['file']
            filename = file.name
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
            content = file.read().decode('utf-8')
            
            directory_id = request.data.get('directory')
            folder_id = request.data.get('folder')
            
            if folder_id:
                try:
                    folder = Folder.objects.get(pk=folder_id)
                    directory_id = folder.directory_id if folder.directory else None
                except Folder.DoesNotExist:
                    return Response(
                        {'error': '指定的文件夹不存在'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            existing_documents = Document.objects.filter(filename=filename)
            if directory_id and folder_id:
                existing_documents = existing_documents.filter(folder_id=folder_id)
            elif directory_id:
                existing_documents = existing_documents.filter(directory_id=directory_id, folder__isnull=True)
            
            if existing_documents.exists():
                return Response(
                    {'error': f'文件 "{filename}" 已存在于当前目录/文件夹中'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            data = {
                'title': title,
                'filename': filename,
                'content': content,
                'directory': directory_id,
                'folder': folder_id
            }
            
            serializer = DocumentSerializer(data=data)
            if serializer.is_valid():
                document = serializer.save()
                DocumentVersion.objects.create(
                    document=document,
                    version_number=1,
                    content=document.content or '',
                    modified_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = DocumentSerializer(data=request.data)
            if serializer.is_valid():
                document = serializer.save()
                DocumentVersion.objects.create(
                    document=document,
                    version_number=1,
                    content=document.content or '',
                    modified_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            old_content = document.content
            serializer = DocumentSerializer(document, data=request.data)
            if serializer.is_valid():
                document = serializer.save()
                if old_content != document.content:
                    latest_version = document.versions.order_by('-version_number').first()
                    new_version_number = latest_version.version_number + 1 if latest_version else 1
                    DocumentVersion.objects.create(
                        document=document,
                        version_number=new_version_number,
                        content=document.content or '',
                        modified_by=request.user,
                        change_summary=request.data.get('change_summary', '')
                    )
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentVersionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id):
        try:
            document = Document.objects.get(pk=document_id)
            versions = document.versions.order_by('-version_number')
            serializer = DocumentVersionSerializer(versions, many=True)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentPublishView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            if document.publish_status == 'published':
                return Response({'error': 'Document is already published'}, status=status.HTTP_400_BAD_REQUEST)
            if document.publish_status == 'pending':
                return Response({'error': 'Document is already in publish queue'}, status=status.HTTP_400_BAD_REQUEST)

            document.publish_status = 'pending'
            document.analysis_status = 'pending'
            document.save(update_fields=['publish_status', 'analysis_status'])

            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentBulkPublishView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        document_ids = request.data.get('document_ids', [])
        
        if not document_ids:
            return Response({'error': 'No document IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取所有文档
        documents = Document.objects.filter(id__in=document_ids)
        if not documents.exists():
            return Response({'error': 'No valid documents found'}, status=status.HTTP_404_NOT_FOUND)
        
        # 过滤掉已经发布或已经在队列中的文档
        docs_to_publish = []
        skipped_docs = []
        
        for doc in documents:
            if doc.publish_status == 'published':
                skipped_docs.append({'id': doc.id, 'title': doc.title, 'reason': 'Already published'})
            elif doc.publish_status == 'pending':
                skipped_docs.append({'id': doc.id, 'title': doc.title, 'reason': 'Already in queue'})
            else:
                docs_to_publish.append(doc)
        
        # 批量更新状态
        if docs_to_publish:
            doc_ids = [d.id for d in docs_to_publish]
            Document.objects.filter(id__in=doc_ids).update(
                publish_status='pending',
                analysis_status='pending'
            )
        
        # 返回结果
        return Response({
            'success_count': len(docs_to_publish),
            'skipped_count': len(skipped_docs),
            'skipped_documents': skipped_docs
        })


class DocumentQueueAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            if document.publish_status != 'published':
                return Response({'error': 'Document must be published before analysis'}, status=status.HTTP_400_BAD_REQUEST)
            if document.analysis_status == 'completed':
                return Response({'error': 'Document analysis is already completed'}, status=status.HTTP_400_BAD_REQUEST)
            if document.analysis_status == 'analyzing':
                return Response({'error': 'Document is already in analysis queue'}, status=status.HTTP_400_BAD_REQUEST)

            document.analysis_status = 'analyzing'
            document.save(update_fields=['analysis_status'])

            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        knowledge_base_id = request.query_params.get('knowledge_base')
        
        queryset = Document.objects.all()
        if knowledge_base_id:
            queryset = queryset.filter(directory__knowledge_base_id=knowledge_base_id)
        
        draft_count = queryset.filter(publish_status='draft').count()
        publishing_count = queryset.filter(publish_status='pending').count()
        
        pending_analysis_count = queryset.filter(analysis_status='pending').count()
        analyzing_count = queryset.filter(analysis_status='analyzing').count()
        
        return Response({
            'draft_count': draft_count,
            'publishing_count': publishing_count,
            'pending_analysis_count': pending_analysis_count,
            'analyzing_count': analyzing_count
        })


class DocumentQueueListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        knowledge_base_id = request.query_params.get('knowledge_base')
        
        queryset = Document.objects.all()
        if knowledge_base_id:
            queryset = queryset.filter(directory__knowledge_base_id=knowledge_base_id)
        
        # 获取所有未发布或待分析的文档
        queue_docs = queryset.filter(
            models.Q(publish_status='draft') | 
            models.Q(publish_status='pending') |
            models.Q(analysis_status='pending') | 
            models.Q(analysis_status='analyzing')
        ).order_by('updated_at')
        
        serializer = DocumentSerializer(queue_docs, many=True)
        return Response(serializer.data)


class MoveDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        directory_id = request.data.get('directory')
        folder_id = request.data.get('folder')
        
        # 验证目标位置是否在同一个知识库
        if directory_id:
            try:
                target_directory = Directory.objects.get(pk=directory_id)
                if document.directory and document.directory.knowledge_base_id != target_directory.knowledge_base_id:
                    return Response({'error': 'Cannot move document to different knowledge base'}, status=status.HTTP_400_BAD_REQUEST)
            except Directory.DoesNotExist:
                return Response({'error': 'Target directory not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if folder_id:
            try:
                target_folder = Folder.objects.get(pk=folder_id)
                if target_folder.directory and document.directory:
                    if target_folder.directory.knowledge_base_id != document.directory.knowledge_base_id:
                        return Response({'error': 'Cannot move document to different knowledge base'}, status=status.HTTP_400_BAD_REQUEST)
            except Folder.DoesNotExist:
                return Response({'error': 'Target folder not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # 更新位置
        document.directory_id = directory_id
        document.folder_id = folder_id
        document.save()
        
        serializer = DocumentSerializer(document)
        return Response(serializer.data)


class MoveFolderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            folder = Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
        
        directory_id = request.data.get('directory')
        parent_id = request.data.get('parent')
        
        # 不能移动到自己或其子文件夹中
        if parent_id:
            if self._is_ancestor_or_self(folder, parent_id):
                return Response({'error': 'Cannot move folder into itself or its subfolders'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证目标位置是否在同一个知识库
        if directory_id:
            try:
                target_directory = Directory.objects.get(pk=directory_id)
                if folder.directory and folder.directory.knowledge_base_id != target_directory.knowledge_base_id:
                    return Response({'error': 'Cannot move folder to different knowledge base'}, status=status.HTTP_400_BAD_REQUEST)
            except Directory.DoesNotExist:
                return Response({'error': 'Target directory not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if parent_id:
            try:
                target_parent = Folder.objects.get(pk=parent_id)
                if target_parent.directory and folder.directory:
                    if target_parent.directory.knowledge_base_id != folder.directory.knowledge_base_id:
                        return Response({'error': 'Cannot move folder to different knowledge base'}, status=status.HTTP_400_BAD_REQUEST)
            except Folder.DoesNotExist:
                return Response({'error': 'Target parent folder not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # 更新位置
        folder.directory_id = directory_id
        folder.parent_id = parent_id
        folder.save()
        
        serializer = FolderSerializer(folder)
        return Response(serializer.data)
    
    def _is_ancestor_or_self(self, folder, target_id):
        """检查目标文件夹是否是当前文件夹或其祖先"""
        if folder.id == target_id:
            return True
        
        current = folder.parent
        while current:
            if current.id == target_id:
                return True
            current = current.parent
        return False


class DocumentTreeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, knowledge_base_id):
        try:
            base = KnowledgeBase.objects.get(pk=knowledge_base_id)
            directory_id = request.query_params.get('directory')
            if directory_id:
                directories = Directory.objects.filter(pk=directory_id, knowledge_base=base)
                if not directories.exists():
                    return Response({'error': 'Directory not found in knowledge base'}, status=status.HTTP_404_NOT_FOUND)
            else:
                directories = Directory.objects.filter(knowledge_base=base)

            tree = []
            for directory in directories:
                folders = Folder.objects.filter(directory=directory, parent__isnull=True)
                dir_data = {
                    'id': directory.id,
                    'name': directory.name,
                    'type': 'directory',
                    'children': self._build_folder_tree(folders, directory)
                }
                documents = Document.objects.filter(directory=directory, folder__isnull=True, publish_status='published')
                for doc in documents:
                    dir_data['children'].append({
                        'id': doc.id,
                        'name': doc.title,
                        'type': 'document',
                        'filename': doc.filename,
                        'publish_status': doc.publish_status,
                        'analysis_status': doc.analysis_status,
                        'updated_at': doc.updated_at.isoformat()
                    })
                tree.append(dir_data)
            return Response(tree)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': 'KnowledgeBase not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def _build_folder_tree(self, folders, directory):
        tree = []
        for folder in folders:
            children = Folder.objects.filter(parent=folder)
            folder_data = {
                'id': folder.id,
                'name': folder.name,
                'type': 'folder',
                'children': self._build_folder_tree(children, directory)
            }
            documents = Document.objects.filter(folder=folder, publish_status='published')
            for doc in documents:
                folder_data['children'].append({
                    'id': doc.id,
                    'name': doc.title,
                    'type': 'document',
                    'filename': doc.filename,
                    'publish_status': doc.publish_status,
                    'analysis_status': doc.analysis_status,
                    'updated_at': doc.updated_at.isoformat()
                })
            tree.append(folder_data)
        return tree


class FullTreeView(APIView):
    """获取完整的文件夹树，用于移动选择"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, knowledge_base_id):
        try:
            base = KnowledgeBase.objects.get(pk=knowledge_base_id)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': 'KnowledgeBase not found'}, status=status.HTTP_404_NOT_FOUND)
        
        tree = []
        directories = Directory.objects.filter(knowledge_base=base)
        
        for directory in directories:
            dir_node = {
                'id': directory.id,
                'name': directory.name,
                'type': 'directory',
                'children': []
            }
            
            # 添加顶级文件夹
            folders = Folder.objects.filter(directory=directory, parent__isnull=True)
            dir_node['children'] = self._build_folder_tree_for_move(folders)
            
            tree.append(dir_node)
        
        return Response(tree)
    
    def _build_folder_tree_for_move(self, folders):
        tree = []
        for folder in folders:
            folder_node = {
                'id': folder.id,
                'name': folder.name,
                'type': 'folder',
                'children': []
            }
            
            # 递归添加子文件夹
            children = folder.children.all()
            folder_node['children'] = self._build_folder_tree_for_move(children)
            
            tree.append(folder_node)
        return tree


class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        directory_id = request.query_params.get('directory')
        user_id = request.query_params.get('user')
        permissions = Permission.objects.all()
        if directory_id:
            permissions = permissions.filter(directory_id=directory_id)
        if user_id:
            permissions = permissions.filter(user_id=user_id)
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PermissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            permission = Permission.objects.get(pk=pk)
            serializer = PermissionSerializer(permission)
            return Response(serializer.data)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            permission = Permission.objects.get(pk=pk)
            serializer = PermissionCreateSerializer(permission, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            permission = Permission.objects.get(pk=pk)
            permission.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        directory_id = request.query_params.get('directory')
        folder_id = request.query_params.get('folder')
        
        if not query.strip():
            return Response([])
        
        search_query = SearchQuery(query, config='chinese')
        search_vector = SearchVector('title', 'content', config='chinese')
        
        documents = Document.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search_vector=search_query,
            publish_status='published'
        ).select_related('directory', 'folder', 'directory__knowledge_base')
        
        if folder_id:
            documents = documents.filter(folder_id=folder_id)
        elif directory_id:
            documents = documents.filter(directory_id=directory_id)
        
        documents = documents.order_by('-rank', '-updated_at')
        
        results = []
        for doc in documents:
            # 构建路径
            path_parts = []
            if doc.directory and doc.directory.knowledge_base:
                path_parts.append(doc.directory.knowledge_base.name)
            if doc.directory:
                path_parts.append(doc.directory.name)
            if doc.folder:
                path_parts.append(doc.folder.name)
            
            # 生成摘要
            summary = self._generate_summary(doc.content, query)
            
            results.append({
                'id': doc.id,
                'title': doc.title,
                'filename': doc.filename,
                'content': doc.content,
                'path': ' / '.join(path_parts) if path_parts else '',
                'summary': summary,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
                'rank': float(doc.rank) if hasattr(doc, 'rank') else 0.0
            })
        
        return Response(results)
    
    def _generate_summary(self, content, query, max_length=200):
        if not content:
            return ''
        
        # 简化版本：找到查询词附近的内容
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 尝试找到查询词的位置
        idx = content_lower.find(query_lower)
        if idx != -1:
            # 从查询词前50个字符开始，后150个字符结束
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query) + 150)
            summary = content[start:end]
            
            # 如果是从中间截取的，添加省略号
            if start > 0:
                summary = '...' + summary
            if end < len(content):
                summary = summary + '...'
            
            return summary
        
        # 如果没找到查询词，返回开头部分
        if len(content) > max_length:
            return content[:max_length] + '...'
        return content


class VectorSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        top_k = int(request.query_params.get('top_k', 5))
        
        if not query.strip():
            return Response([])
        
        from .models import DocumentChunk
        from .embedding import get_embedding, cosine_similarity
        from api.models import AIConfig
        import json
        
        chunks = DocumentChunk.objects.filter(
            document__publish_status='published',
            embedding__isnull=False
        ).select_related('document')
        
        ai_config = AIConfig.objects.first()
        if not ai_config or not ai_config.embedding_api_key:
            return Response([])
        
        query_embedding = get_embedding(
            query,
            ai_config.embedding_api_key,
            ai_config.embedding_base_url,
            ai_config.embedding_model_name
        )
        
        if query_embedding is None:
            return Response([])
        
        results = []
        for chunk in chunks:
            try:
                chunk_embedding = json.loads(chunk.embedding)
                similarity = cosine_similarity(query_embedding, chunk_embedding)
                results.append({
                    'chunk_id': chunk.id,
                    'document_id': chunk.document.id,
                    'document_title': chunk.document.title,
                    'content': chunk.content,
                    'similarity': similarity,
                    'chunk_index': chunk.chunk_index
                })
            except (json.JSONDecodeError, TypeError):
                continue
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return Response(results[:top_k])


from .storage_service import StorageService
from .document_converter import DocumentConverter
from .storage_models import FileStorage, FileAttachment, DocumentConversion
from .serializers import DocumentSerializer
from django.conf import settings
from django.http import FileResponse
import os
import zipfile
import io


def normalize_zip_filename(filename):
    """保证ZIP条目路径使用UTF-8解码，兼容GBK/CP437编码的中文文件名。"""
    if isinstance(filename, bytes):
        for enc in ('utf-8', 'gbk', 'cp936', 'cp437'):
            try:
                return filename.decode(enc)
            except UnicodeDecodeError:
                continue
        return filename.decode('utf-8', errors='ignore')

    if isinstance(filename, str):
        try:
            raw = filename.encode('cp437')
            return raw.decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                raw = filename.encode('cp437')
                return raw.decode('gbk')
            except (UnicodeEncodeError, UnicodeDecodeError):
                return filename

    return filename


def _handle_single_file_import(file_obj, directory_id, folder_id, user):
    """处理单个文件导入的通用逻辑，供单文件上传和ZIP导入共同使用"""
    print(f'_handle_single_file_import 开始: directory_id={directory_id}, folder_id={folder_id}')
    
    # 创建新文档
    filename = file_obj.name
    title = filename.rsplit('.', 1)[0] if '.' in filename else filename
    file_ext = os.path.splitext(filename)[1].lower()
    
    # 对于md和txt文件，直接读取内容
    initial_content = ''
    if file_ext in ['.md', '.txt']:
        try:
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
                content_bytes = file_obj.read()
                initial_content = content_bytes.decode('utf-8')
                print(f'直接读取文件内容，长度: {len(initial_content)}')
        except Exception as e:
            print(f'读取文件内容失败: {e}')
    
    # 直接创建Document对象，避免序列化器问题
    try:
        directory = None
        if directory_id:
            directory = Directory.objects.get(id=directory_id)
        
        folder = None
        if folder_id:
            folder = Folder.objects.get(id=folder_id)
        
        document = Document.objects.create(
            title=title,
            filename=filename,
            content=initial_content,  # 直接设置初始内容
            directory=directory,
            folder=folder
        )
        print(f'创建Document对象成功: {document.id}, 初始内容长度: {len(initial_content)}')
        
        # 创建文档版本
        DocumentVersion.objects.create(
            document=document,
            version_number=1,
            content=initial_content,  # 也设置到version中
            modified_by=user
        )
        print('创建DocumentVersion成功')
        
        # 保存原始文件
        file_storage = StorageService.save_file(
            file_obj=file_obj,
            storage_type='original',
            document=document,
            original_name=filename
        )
        print(f'保存文件成功: {file_storage.id}')
        print(f'file_storage.document_id: {file_storage.document_id}')
        
        # 确保file_storage正确关联了document
        if file_storage.document_id != document.id:
            print(f'更新file_storage的document关联')
            file_storage.document = document
            file_storage.save()
        
        # 对于非md/txt文件，还是需要转换
        if file_ext not in ['.md', '.txt']:
            print('开始转换...')
            result = DocumentConverter.convert_async(file_storage.id)
            print(f'转换结果: {result}')
            
            # 重新从数据库获取document，确保内容已更新
            document.refresh_from_db()
            print(f'转换后文档内容长度: {len(document.content)}')
        
        return {
            'success': True,
            'document': document,
            'file_storage': file_storage
        }
    except Exception as e:
        import traceback
        print(f'_handle_single_file_import 错误: {str(e)}')
        print(traceback.format_exc())
        return {
            'success': False,
            'error': str(e)
        }


class FileUploadView(APIView):
    """文件上传API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': '没有文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        document_id = request.data.get('document_id')
        directory_id = request.data.get('directory_id')
        folder_id = request.data.get('folder_id')
        create_document = request.data.get('create_document', True)
        
        # 获取文档对象
        document = None
        if document_id:
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 保存原始文件
            file_storage = StorageService.save_file(
                file_obj=file_obj,
                storage_type='original',
                document=document,
                original_name=file_obj.name
            )
            
            # 开始转换
            result = DocumentConverter.convert_async(file_storage.id)
            
            return Response({
                'file_id': file_storage.id,
                'md5': file_storage.md5_hash,
                'file_name': file_storage.file_name,
                'status': result.get('success', False),
                'conversion_result': result,
                'document_id': document.id
            })
        
        elif create_document:
            # 使用统一的导入函数
            result = _handle_single_file_import(file_obj, directory_id, folder_id, request.user)
            
            if not result['success']:
                return Response(result['error'], status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'file_id': result['file_storage'].id,
                'md5': result['file_storage'].md5_hash,
                'file_name': result['file_storage'].file_name,
                'status': True,
                'document_id': result['document'].id
            })
        
        return Response({'error': '未指定文档或未要求创建文档'}, status=status.HTTP_400_BAD_REQUEST)


class FileUploadMultipleView(APIView):
    """批量文件上传API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'files' not in request.FILES:
            return Response({'error': '没有文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        files = request.FILES.getlist('files')
        document_id = request.data.get('document_id')
        directory_id = request.data.get('directory_id')
        folder_id = request.data.get('folder_id')
        create_document = request.data.get('create_document', True)
        
        results = []
        for file_obj in files:
            # 获取文档对象
            document = None
            if document_id:
                try:
                    document = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    continue
                
                # 保存原始文件
                file_storage = StorageService.save_file(
                    file_obj=file_obj,
                    storage_type='original',
                    document=document,
                    original_name=file_obj.name
                )
                
                # 开始转换
                conversion_result = DocumentConverter.convert_async(file_storage.id)
                
                results.append({
                    'file_id': file_storage.id,
                    'md5': file_storage.md5_hash,
                    'file_name': file_storage.file_name,
                    'status': conversion_result.get('success', False),
                    'document_id': document.id
                })
            
            elif create_document:
                # 使用统一的导入函数
                import_result = _handle_single_file_import(file_obj, directory_id, folder_id, request.user)
                
                if import_result['success']:
                    results.append({
                        'file_id': import_result['file_storage'].id,
                        'md5': import_result['file_storage'].md5_hash,
                        'file_name': import_result['file_storage'].file_name,
                        'status': True,
                        'document_id': import_result['document'].id
                    })
                else:
                    results.append({
                        'file_name': file_obj.name,
                        'status': False,
                        'error': import_result.get('error', '导入失败')
                    })
        
        return Response({'files': results})


class FileAccessView(APIView):
    """文件访问API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, md5_hash):
        file_storage = StorageService.get_file(md5_hash)
        if not file_storage:
            return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = file_storage.full_path
        if not os.path.exists(file_path):
            return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            open(file_path, 'rb'),
            filename=file_storage.file_name,
            content_type=file_storage.mime_type or 'application/octet-stream'
        )


class FileInfoView(APIView):
    """文件信息API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, file_id):
        file_storage = StorageService.get_file_by_id(file_id)
        if not file_storage:
            return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': file_storage.id,
            'md5_hash': file_storage.md5_hash,
            'file_name': file_storage.file_name,
            'file_size': file_storage.file_size,
            'file_type': file_storage.file_type,
            'mime_type': file_storage.mime_type,
            'storage_type': file_storage.storage_type,
            'file_url': file_storage.file_url,
            'created_at': file_storage.created_at,
            'updated_at': file_storage.updated_at,
            'document_id': file_storage.document_id
        })


class DocumentAttachmentListView(APIView):
    """文档附件列表API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        attachments = FileAttachment.objects.filter(document=document)
        
        return Response([{
            'id': attachment.id,
            'original_name': attachment.original_name,
            'description': attachment.description,
            'position': attachment.position,
            'created_at': attachment.created_at,
            'file_id': attachment.file_storage.id,
            'file_url': attachment.file_storage.file_url,
            'file_name': attachment.file_storage.file_name,
            'file_size': attachment.file_storage.file_size
        } for attachment in attachments])


class ConversionStatusView(APIView):
    """转换状态查询API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversion_id):
        try:
            conversion = DocumentConversion.objects.get(id=conversion_id)
        except DocumentConversion.DoesNotExist:
            return Response({'error': '转换记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': conversion.id,
            'status': conversion.status,
            'original_file_id': conversion.original_file.id,
            'original_file_name': conversion.original_file.file_name,
            'converted_file_id': conversion.converted_file.id if conversion.converted_file else None,
            'converted_file_name': conversion.converted_file.file_name if conversion.converted_file else None,
            'error_message': conversion.error_message,
            'conversion_info': conversion.conversion_info,
            'started_at': conversion.started_at,
            'completed_at': conversion.completed_at,
            'created_at': conversion.created_at
        })


# ==================== AI Chat Views ====================

from .chat_models import ChatSession, ChatMessage
from .bm25 import search_fulltext, search_vector, search_hybrid
from api.models import AIConfig
import openai
import json


class BM25SearchView(APIView):
    """全文检索API（使用PostgreSQL全文索引）"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        top_k = int(request.query_params.get('top_k', 5))
        knowledge_base_id = request.query_params.get('knowledge_base_id')
        
        if not query.strip():
            return Response([])
        
        # 使用数据库全文索引搜索
        results = search_fulltext(query, knowledge_base_id=knowledge_base_id, top_k=top_k)
        
        # 格式化结果
        formatted_results = []
        for doc_id, score, title, content in results:
            # 获取文档预览（前200字符）
            preview = content[:200] + '...' if len(content) > 200 else content
            formatted_results.append({
                'document_id': doc_id,
                'title': title,
                'content': preview,
                'full_content': content,
                'score': float(score)
            })
        
        return Response(formatted_results)


class VectorSearchAPIView(APIView):
    """向量检索API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        top_k = int(request.query_params.get('top_k', 5))
        knowledge_base_id = request.query_params.get('knowledge_base_id')
        
        if not query.strip():
            return Response([])
        
        # 使用向量检索
        results = search_vector(query, knowledge_base_id=knowledge_base_id, top_k=top_k)
        
        # 格式化结果
        formatted_results = []
        for doc_id, score, title, content in results:
            # 获取文档预览（前200字符）
            preview = content[:200] + '...' if len(content) > 200 else content
            formatted_results.append({
                'document_id': doc_id,
                'title': title,
                'content': preview,
                'full_content': content,
                'score': float(score)
            })
        
        return Response(formatted_results)


class HybridSearchView(APIView):
    """混合检索API（全文+向量）"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        top_k = int(request.query_params.get('top_k', 5))
        knowledge_base_id = request.query_params.get('knowledge_base_id')
        fulltext_weight = float(request.query_params.get('fulltext_weight', 0.5))
        vector_weight = float(request.query_params.get('vector_weight', 0.5))
        
        if not query.strip():
            return Response([])
        
        # 使用混合检索
        results = search_hybrid(
            query, 
            knowledge_base_id=knowledge_base_id, 
            top_k=top_k,
            fulltext_weight=fulltext_weight,
            vector_weight=vector_weight
        )
        
        # 格式化结果
        formatted_results = []
        for doc_id, score, title, content in results:
            # 获取文档预览（前200字符）
            preview = content[:200] + '...' if len(content) > 200 else content
            formatted_results.append({
                'document_id': doc_id,
                'title': title,
                'content': preview,
                'full_content': content,
                'score': float(score)
            })
        
        return Response(formatted_results)


class ChatSessionListView(APIView):
    """会话列表API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        knowledge_base_id = request.query_params.get('knowledge_base_id')
        
        sessions = ChatSession.objects.filter(user=request.user)
        if knowledge_base_id:
            sessions = sessions.filter(knowledge_base_id=knowledge_base_id)
        
        results = []
        for session in sessions:
            latest_message = session.messages.order_by('-created_at').first()
            results.append({
                'id': session.id,
                'title': session.title,
                'knowledge_base_id': session.knowledge_base.id,
                'knowledge_base_name': session.knowledge_base.name,
                'latest_message': latest_message.content[:50] + '...' if latest_message else '',
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })
        
        return Response(results)
    
    def post(self, request):
        knowledge_base_id = request.data.get('knowledge_base_id')
        title = request.data.get('title', '新对话')
        
        if not knowledge_base_id:
            return Response({'error': '需要指定知识库'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .models import KnowledgeBase
            knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id)
        except KnowledgeBase.DoesNotExist:
            return Response({'error': '知识库不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        session = ChatSession.objects.create(
            user=request.user,
            knowledge_base=knowledge_base,
            title=title
        )
        
        return Response({
            'id': session.id,
            'title': session.title,
            'knowledge_base_id': knowledge_base.id,
            'created_at': session.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class ChatSessionDetailView(APIView):
    """会话详情API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            session = ChatSession.objects.get(id=pk, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = []
        for msg in session.messages.all():
            messages.append({
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'retrieved_documents': msg.retrieved_documents,
                'created_at': msg.created_at.isoformat()
            })
        
        return Response({
            'id': session.id,
            'title': session.title,
            'knowledge_base_id': session.knowledge_base.id,
            'knowledge_base_name': session.knowledge_base.name,
            'messages': messages,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        })
    
    def delete(self, request, pk):
        try:
            session = ChatSession.objects.get(id=pk, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatSendMessageView(APIView):
    """发送消息API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        user_content = request.data.get('content', '')
        if not user_content.strip():
            return Response({'error': '消息内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存用户消息
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_content
        )
        
        # 使用混合检索（全文+向量）检索相关文档
        # 如果向量检索失败，回退到全文检索
        search_results = search_hybrid(
            user_content, 
            knowledge_base_id=session.knowledge_base.id, 
            top_k=3,
            fulltext_weight=0.4,
            vector_weight=0.6
        )
        # 如果混合检索没有结果，尝试只用全文检索
        if not search_results:
            search_results = search_fulltext(user_content, knowledge_base_id=session.knowledge_base.id, top_k=3)
        
        retrieved_docs = []
        context_parts = []
        for i, (doc_id, score, title, content) in enumerate(search_results, 1):
            doc_info = {
                'document_id': doc_id,
                'title': title,
                'content': content,
                'score': float(score)
            }
            retrieved_docs.append(doc_info)
            context_parts.append(f"【文档{i}：{title}】\n{content}")
        
        context = "\n\n".join(context_parts)
        
        # 获取历史对话
        history_messages = session.messages.exclude(id=user_message.id).order_by('created_at')
        history = []
        for msg in history_messages:
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # 生成AI回复
        ai_response = self._generate_response(user_content, context, history)
        
        # 保存助手消息
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response,
            retrieved_documents=retrieved_docs
        )
        
        # 更新会话标题（如果是第一条消息）
        if session.messages.count() <= 2:
            session.title = user_content[:30] + '...' if len(user_content) > 30 else user_content
            session.save()
        
        return Response({
            'user_message': {
                'id': user_message.id,
                'role': user_message.role,
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_message.id,
                'role': assistant_message.role,
                'content': assistant_message.content,
                'retrieved_documents': retrieved_docs,
                'created_at': assistant_message.created_at.isoformat()
            }
        })
    
    def _generate_response(self, user_query: str, context: str, history: list) -> str:
        """生成AI回复"""
        ai_config = AIConfig.objects.first()
        
        if not ai_config or not ai_config.text_generation_api_key:
            return "AI助手未配置，请先在设置中配置API密钥。"
        
        try:
            client = openai.OpenAI(
                api_key=ai_config.text_generation_api_key,
                base_url=ai_config.text_generation_base_url
            )
            
            system_prompt = """你是一个专业的知识库助手。请根据提供的文档内容回答用户的问题。

回答要求：
1. 只使用提供的文档内容进行回答，不要编造信息
2. 如果文档中没有相关信息，请明确说明
3. 回答要简洁准确，重点突出
4. 可以适当引用文档内容作为依据
5. 保持友好和专业的语气"""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加历史对话
            messages.extend(history)
            
            # 添加当前查询和上下文
            if context:
                user_content = f"请根据以下文档回答我的问题：\n\n{context}\n\n我的问题是：{user_query}"
            else:
                user_content = user_query
            
            messages.append({"role": "user", "content": user_content})
            
            # 用 requests 直接调用，完全控制请求格式（兼容 LM Studio）
            
            payload = {
                "model": ai_config.text_generation_model_name,
                "messages": messages,
                "temperature": ai_config.text_generation_temperature,
                "max_tokens": 2000,
                "top_p": 0.95,
                "chat_template_kwargs": {"enable_thinking": False}
            }
            
            response = requests.post(
                f"{ai_config.text_generation_base_url}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {ai_config.text_generation_api_key}"},
                timeout=120.0
            )
            
            response.raise_for_status()  # 检查 HTTP 错误
            data = response.json()
            message = data["choices"][0]["message"]
            
            # 智能提取响应内容
            content_candidate = None
            
            # 1. 优先尝试 content
            if message.get("content") and message["content"].strip():
                content_candidate = message["content"].strip()
            
            # 2. 然后尝试 reasoning_content
            if not content_candidate and message.get("reasoning_content"):
                rc = message["reasoning_content"].strip()
                # 尝试从 reasoning_content 中提取最终回答
                # 查找最后的中文或英文回答
                lines = [line.strip() for line in rc.split('\n') if line.strip()]
                if lines:
                    # 优先查找看起来像回答的行（不是思考过程的行）
                    for line in reversed(lines):
                        if not line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and not line.startswith(('*', '-')) and not line.startswith(('Here', '**')):
                            content_candidate = line
                            break
                    # 如果没找到，就用最后一行
                    if not content_candidate:
                        content_candidate = lines[-1]
            
            if content_candidate:
                return content_candidate
            
            return str(message)
            
        except Exception as e:
            return f"抱歉，生成回复时出错：{str(e)}"


class ZipUploadView(APIView):
    """上传并解析zip文件API"""
    permission_classes = [IsAuthenticated]
    
    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        '.md', '.txt', '.docx', '.doc', '.pptx', '.ppt', 
        '.pdf', '.xlsx', '.xls'
    }
    
    def post(self, request):
        print('=== ZipUploadView POST 开始 ===')
        print('request.FILES:', request.FILES)
        print('request.FILES keys:', list(request.FILES.keys()))
        print('request.POST:', request.POST)
        
        if 'zip_file' not in request.FILES:
            # 尝试查找其他可能的key名
            if len(request.FILES) > 0:
                first_key = list(request.FILES.keys())[0]
                print(f'找到文件，key是: {first_key}')
                zip_file = request.FILES[first_key]
            else:
                return Response({'error': '没有上传zip文件'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            zip_file = request.FILES['zip_file']
        
        # 检查文件类型
        if not zip_file.name.endswith('.zip'):
            return Response({'error': '只能上传zip格式的文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 读取zip文件内容
            zip_content = zip_file.read()
            zip_buffer = io.BytesIO(zip_content)
            
            # 解析zip文件
            file_list = []
            skipped_count = 0
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                # 先检查是否有顶层文件夹（所有文件是否都在同一个文件夹下）
                all_paths = []
                for info in zf.infolist():
                    if info.filename.startswith('__MACOSX') or info.filename.startswith('.'):
                        continue
                    # 清理路径，去除末尾的/
                    cleaned_path = info.filename.rstrip('/')
                    cleaned_path = normalize_zip_filename(cleaned_path)
                    if cleaned_path:
                        all_paths.append(cleaned_path)
                
                print('ZIP中的所有路径:', all_paths)
                
                # 检查是否所有文件都在同一个顶层文件夹下
                top_level_dir = None
                if all_paths:
                    first_path_parts = all_paths[0].split('/')
                    if len(first_path_parts) > 1:  # 第一个文件有父文件夹
                        potential_top_dir = first_path_parts[0]
                        # 检查所有其他文件是否都在这个文件夹下
                        all_in_same_dir = True
                        for path in all_paths:
                            path_parts = path.split('/')
                            if len(path_parts) > 0 and path_parts[0] != potential_top_dir:
                                all_in_same_dir = False
                                break
                        if all_in_same_dir:
                            top_level_dir = potential_top_dir
                            print(f'检测到顶层文件夹: {top_level_dir}')
                
                # 现在处理文件
                for info in zf.infolist():
                    # 跳过目录项和隐藏文件
                    if info.is_dir() or info.filename.startswith('__MACOSX') or info.filename.startswith('.'):
                        continue
                    
                    # 获取文件路径信息
                    original_path = info.filename.rstrip('/')
                    original_path = normalize_zip_filename(original_path)
                    path_parts = original_path.split('/')
                    filename = path_parts[-1]
                    
                    # 跳过空文件名
                    if not filename:
                        continue
                    
                    # 检查文件扩展名是否支持
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext not in self.SUPPORTED_EXTENSIONS:
                        skipped_count += 1
                        continue
                    
                    # 构建相对路径（不包含文件名）
                    # 如果有顶层文件夹，我们保留它
                    relative_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
                    
                    print(f'处理文件: {original_path} -> 相对路径: {relative_path}, 文件名: {filename}')
                    
                    file_list.append({
                        'filename': filename,
                        'path': original_path,  # 使用原始路径作为唯一标识
                        'relative_path': relative_path,
                        'size': info.file_size,
                        'selected': True  # 默认选中
                    })
            
            return Response({
                'files': file_list,
                'total_files': len(file_list),
                'skipped_count': skipped_count
            })
            
        except zipfile.BadZipFile:
            return Response({'error': '无效的zip文件'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(f'解析ZIP出错: {str(e)}')
            print(traceback.format_exc())
            return Response({'error': f'解析zip文件失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZipImportView(APIView):
    """执行zip文件导入API"""
    permission_classes = [IsAuthenticated]
    
    # 支持的文件类型（与 ZipUploadView 保持一致）
    SUPPORTED_EXTENSIONS = {
        '.md', '.txt', '.docx', '.doc', '.pptx', '.ppt', 
        '.pdf', '.xlsx', '.xls'
    }
    
    def post(self, request):
        print('=== ZipImportView POST 开始 ===')
        print('request.FILES:', request.FILES)
        print('request.POST:', request.POST)
        print('request.data:', request.data)
        
        if 'zip_file' not in request.FILES:
            return Response({'error': '没有上传zip文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        zip_file = request.FILES['zip_file']
        
        # 处理selected_files，支持JSON字符串和列表
        # 先从request.POST获取，因为FormData数据在这里
        selected_files_raw = request.POST.get('selected_files', '[]')
        if isinstance(selected_files_raw, str):
            import json
            try:
                selected_files = json.loads(selected_files_raw)
            except:
                selected_files = []
        else:
            selected_files = selected_files_raw or []
        
        print('selected_files:', selected_files)
        
        # 获取directory_id和folder_id
        directory_id = request.POST.get('directory_id')
        folder_id = request.POST.get('folder_id')
        
        # 如果POST中没有，尝试从data获取
        if not directory_id and hasattr(request, 'data'):
            directory_id = request.data.get('directory_id')
        if not folder_id and hasattr(request, 'data'):
            folder_id = request.data.get('folder_id')
        
        print('directory_id:', directory_id)
        print('folder_id:', folder_id)
        
        if not selected_files:
            return Response({'error': '没有选择要导入的文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取目录
        directory = None
        if directory_id:
            try:
                # 确保是整数
                dir_id = int(directory_id)
                directory = Directory.objects.get(id=dir_id)
                print('找到目录:', directory)
            except Directory.DoesNotExist:
                return Response({'error': '目录不存在'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': '无效的目录ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前文件夹
        current_folder = None
        if folder_id:
            try:
                # 确保是整数
                fld_id = int(folder_id)
                current_folder = Folder.objects.get(id=fld_id)
                print('找到文件夹:', current_folder)
                if not directory:
                    directory = current_folder.directory
            except Folder.DoesNotExist:
                return Response({'error': '文件夹不存在'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': '无效的文件夹ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not directory:
            return Response({'error': '请选择要导入到的目录'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            zip_content = zip_file.read()
            zip_buffer = io.BytesIO(zip_content)
            
            results = []
            # 清理selected_paths中的路径，统一为UTF-8编码路径
            cleaned_selected_paths = set()
            for path in selected_files:
                normalized_path = normalize_zip_filename(path).rstrip('/')
                cleaned_selected_paths.add(normalized_path)
            print(f'清理后的选中路径: {cleaned_selected_paths}')
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                for info in zf.infolist():
                    # 清理当前文件的路径
                    cleaned_current_path = info.filename.rstrip('/')
                    cleaned_current_path = normalize_zip_filename(cleaned_current_path)
                    
                    if info.is_dir() or cleaned_current_path not in cleaned_selected_paths:
                        continue
                    
                    # 获取文件名
                    path_parts = cleaned_current_path.split('/')
                    filename = path_parts[-1]
                    
                    # 再次检查文件扩展名（安全措施）
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext not in self.SUPPORTED_EXTENSIONS:
                        continue
                    
                    try:
                        print(f"\n=== 开始处理文件: {cleaned_current_path} ===")
                        
                        # 解析路径
                        relative_path_parts = path_parts[:-1] if len(path_parts) > 1 else []
                        print(f"路径部分: {relative_path_parts}")
                        
                        # 创建文件夹结构
                        parent_folder = current_folder
                        print(f"初始父文件夹: {parent_folder.id if parent_folder else 'None'} ({parent_folder.name if parent_folder else '根目录'})")
                        
                        for folder_name in relative_path_parts:
                            if not folder_name:
                                continue
                            
                            print(f"处理文件夹: {folder_name} (父文件夹: {parent_folder.id if parent_folder else 'None'})")
                            
                            # 查找或创建文件夹
                            existing_folder = Folder.objects.filter(
                                directory=directory,
                                parent=parent_folder,
                                name=folder_name
                            ).first()
                            
                            if existing_folder:
                                print(f"文件夹已存在: {existing_folder.id} - {existing_folder.name} (父: {existing_folder.parent.id if existing_folder.parent else 'None'})")
                                parent_folder = existing_folder
                            else:
                                new_folder = Folder.objects.create(
                                    directory=directory,
                                    parent=parent_folder,
                                    name=folder_name
                                )
                                print(f"创建新文件夹: {new_folder.id} - {new_folder.name} (父: {new_folder.parent.id if new_folder.parent else 'None'})")
                                parent_folder = new_folder
                        
                        print(f"最终父文件夹: {parent_folder.id if parent_folder else 'None'}")
                        
                        # 读取文件内容
                        file_content = zf.read(info)
                        file_obj = io.BytesIO(file_content)
                        file_obj.name = filename
                        
                        # 使用统一的导入函数
                        import_result = _handle_single_file_import(
                            file_obj,
                            directory.id,
                            parent_folder.id if parent_folder else None,
                            request.user
                        )
                        
                        if import_result['success']:
                            results.append({
                                'path': info.filename,
                                'status': 'success',
                                'document_id': import_result['document'].id,
                                'folder_id': parent_folder.id if parent_folder else None,
                                'directory_id': directory.id
                            })
                            print(f"✅ 文件处理成功: {info.filename}")
                        else:
                            results.append({
                                'path': info.filename,
                                'status': 'error',
                                'error': str(import_result.get('error', '导入失败'))
                            })
                            print(f"❌ 文件处理失败: {info.filename}")
                        
                    except Exception as e:
                        import traceback
                        error_trace = traceback.format_exc()
                        print(f"❌ 处理文件失败: {info.filename}")
                        print(f"错误: {str(e)}")
                        print(f"堆栈:\n{error_trace}")
                        results.append({
                            'path': info.filename,
                            'status': 'error',
                            'error': str(e)
                        })
            
            success_count = sum(1 for r in results if r['status'] == 'success')
            
            return Response({
                'success': True,
                'results': results,
                'success_count': success_count,
                'total_count': len(results)
            })
            
        except zipfile.BadZipFile:
            return Response({'error': '无效的zip文件'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'导入zip文件失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

