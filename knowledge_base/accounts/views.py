from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, UserPermission
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    UserWithPermissionsSerializer,
    UpdateUserPermissionsSerializer
)
from documents.models import KnowledgeBase, Directory


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser and request.user.role != 'superuser':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        if not request.user.is_superuser and request.user.role != 'superuser':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = CustomUser.objects.get(pk=pk)
            serializer = UserWithPermissionsSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        if not request.user.is_superuser and request.user.role != 'superuser':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = CustomUser.objects.get(pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        if not request.user.is_superuser and request.user.role != 'superuser':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = CustomUser.objects.get(pk=pk)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        if not request.user.is_superuser and request.user.role != 'superuser':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = CustomUser.objects.get(pk=user_id)
            permissions = UserPermission.objects.filter(user=user)
            knowledge_base_ids = [p.knowledge_base_id for p in permissions if p.knowledge_base_id]
            directory_ids = [p.directory_id for p in permissions if p.directory_id]
            return Response({
                'user_id': user.id,
                'knowledge_base_ids': knowledge_base_ids,
                'directory_ids': directory_ids
            })
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, user_id):
        if not request.user.is_superuser and request.user.role != 'superuser':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = CustomUser.objects.get(pk=user_id)
            serializer = UpdateUserPermissionsSerializer(data=request.data)
            if serializer.is_valid():
                # 删除旧的权限
                UserPermission.objects.filter(user=user).delete()
                
                # 添加新的知识库权限
                for kb_id in serializer.validated_data['knowledge_base_ids']:
                    try:
                        kb = KnowledgeBase.objects.get(pk=kb_id)
                        UserPermission.objects.create(user=user, knowledge_base=kb)
                    except KnowledgeBase.DoesNotExist:
                        continue
                
                # 添加新的目录权限
                for dir_id in serializer.validated_data['directory_ids']:
                    try:
                        directory = Directory.objects.get(pk=dir_id)
                        UserPermission.objects.create(user=user, directory=directory)
                    except Directory.DoesNotExist:
                        continue
                
                return Response({'success': True})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)