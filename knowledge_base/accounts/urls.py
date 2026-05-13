from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    UserProfileView,
    UserListView,
    UserDetailView,
    UserPermissionsView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/permissions/', UserPermissionsView.as_view(), name='user-permissions'),
]