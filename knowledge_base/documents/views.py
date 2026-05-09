from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
        if directory_id:
            documents = documents.filter(directory_id=directory_id)
        if folder_id:
            documents = documents.filter(folder_id=folder_id)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    def post(self, request):
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
                        'analysis_status': doc.analysis_status
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
                    'analysis_status': doc.analysis_status
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