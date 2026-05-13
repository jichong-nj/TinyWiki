from rest_framework import serializers
from .models import KnowledgeBase, Directory, Folder, Document, DocumentVersion, Permission


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class DirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = ['id', 'knowledge_base', 'name', 'description', 'order', 'created_at', 'updated_at']


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'directory', 'parent', 'name', 'order', 'created_at', 'updated_at']


class DocumentVersionSerializer(serializers.ModelSerializer):
    modified_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = ['id', 'document', 'version_number', 'content', 'modified_by', 'change_summary', 'created_at']
        read_only_fields = ['id', 'document', 'version_number', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    current_version = serializers.SerializerMethodField()
    directory = serializers.PrimaryKeyRelatedField(queryset=Directory.objects.all(), allow_null=True, required=False)
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all(), allow_null=True, required=False)
    
    class Meta:
        model = Document
        fields = ['id', 'directory', 'folder', 'title', 'filename', 'content', 'order', 'publish_status', 'analysis_status', 'created_at', 'updated_at', 'current_version']
    
    def get_current_version(self, obj):
        current = obj.get_current_version()
        if current:
            return DocumentVersionSerializer(current).data
        return None


class PermissionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    directory = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'user', 'directory', 'role', 'created_at']


class PermissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['user', 'directory', 'role']