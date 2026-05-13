from rest_framework import serializers
from .models import CustomUser, UserPermission
from documents.models import KnowledgeBase, Directory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'avatar', 'bio', 'role', 'date_joined', 'is_superuser']
        read_only_fields = ['id', 'date_joined', 'is_superuser']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'role': {'required': False}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserPermissionSerializer(serializers.ModelSerializer):
    knowledge_base_name = serializers.CharField(source='knowledge_base.name', read_only=True)
    directory_name = serializers.CharField(source='directory.name', read_only=True)
    
    class Meta:
        model = UserPermission
        fields = ['id', 'user', 'knowledge_base', 'knowledge_base_name', 'directory', 'directory_name']


class UserWithPermissionsSerializer(serializers.ModelSerializer):
    permissions = UserPermissionSerializer(source='assigned_permissions', many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'avatar', 'bio', 'role', 'date_joined', 'permissions']
        read_only_fields = ['id', 'date_joined']


class UpdateUserPermissionsSerializer(serializers.Serializer):
    knowledge_base_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    directory_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )