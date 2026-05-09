from django.urls import path, include
from . import views

urlpatterns = [
    path('documents/', include('documents.urls')),
    path('ai/test-model/', views.test_model, name='test_model'),
    path('ai/config/', views.save_ai_config, name='save_ai_config'),
    path('system/config/', views.save_system_config, name='save_system_config'),
]