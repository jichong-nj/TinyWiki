from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
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
        folders = Folder.objects.all()
        if directory_id:
            folders = folders.filter(directory_id=directory_id)
        if parent_id:
            folders = folders.filter(parent_id=parent_id)
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
            document.publish_status = 'published'
            document.analysis_status = 'analyzing'
            document.save()
            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


class DocumentTreeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, knowledge_base_id):
        try:
            base = KnowledgeBase.objects.get(pk=knowledge_base_id)
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
                documents = Document.objects.filter(directory=directory, folder__isnull=True)
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
            documents = Document.objects.filter(folder=folder)
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
        )
        
        if folder_id:
            documents = documents.filter(folder_id=folder_id)
        elif directory_id:
            documents = documents.filter(directory_id=directory_id)
        
        documents = documents.order_by('-rank', '-updated_at')
        
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)


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
from django.conf import settings
from django.http import FileResponse
import os


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
        elif create_document:
            # 创建新文档
            filename = file_obj.name
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
            
            data = {
                'title': title,
                'filename': filename,
                'content': '',
                'directory': directory_id,
                'folder': folder_id
            }
            
            serializer = DocumentSerializer(data=data)
            if serializer.is_valid():
                document = serializer.save()
                DocumentVersion.objects.create(
                    document=document,
                    version_number=1,
                    content='',
                    modified_by=request.user
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
            'document_id': document.id if document else None
        })


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
            elif create_document:
                # 创建新文档
                filename = file_obj.name
                title = filename.rsplit('.', 1)[0] if '.' in filename else filename
                
                data = {
                    'title': title,
                    'filename': filename,
                    'content': '',
                    'directory': directory_id,
                    'folder': folder_id
                }
                
                serializer = DocumentSerializer(data=data)
                if serializer.is_valid():
                    document = serializer.save()
                    DocumentVersion.objects.create(
                        document=document,
                        version_number=1,
                        content='',
                        modified_by=request.user
                    )
                else:
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
                'document_id': document.id if document else None
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
