from django.urls import path, include
from . import views

urlpatterns = [
    path('documents/', include('documents.urls')),
    path('ai/test-model/', views.test_model, name='test_model'),
    path('ai/config/', views.ai_config, name='ai_config'),
    path('system/config/', views.system_config, name='system_config'),
    path('openclaw/agents/', views.OpenClawAgentsView.as_view(), name='openclaw_agents'),
    path('openclaw/chat/', views.OpenClawChatView.as_view(), name='openclaw_chat'),
]