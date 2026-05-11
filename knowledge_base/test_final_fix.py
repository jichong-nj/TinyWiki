#!/usr/bin/env python3
"""测试最终修复"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')
django.setup()

from api.models import AIConfig
from documents.models import KnowledgeBase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from documents.chat_models import ChatSession
import openai
import json

print("=" * 60)
print("测试最终修复")
print("=" * 60)
print()

# 1. 测试 OpenAI SDK 调用
print("1. 测试 OpenAI SDK 调用...")
try:
    config = AIConfig.objects.first()
    client = openai.OpenAI(
        api_key=config.text_generation_api_key,
        base_url=config.text_generation_base_url
    )
    
    # 先测试一下SDK是否支持extra_body
    print("   SDK版本:", openai.__version__)
    
    # 尝试直接构造，不用SDK
    print("   用 requests 直接测试...")
    import requests
    
    payload = {
        "model": config.text_generation_model_name,
        "messages": [
            {"role": "system", "content": "你是一个专业的知识库助手"},
            {"role": "user", "content": "你好，请用中文简短回复"}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.95,
        "chat_template_kwargs": {"enable_thinking": False}
    }
    
    response = requests.post(
        f"{config.text_generation_base_url}/chat/completions",
        json=payload,
        timeout=60
    )
    data = response.json()
    print(f"   ✅ 成功！")
    msg = data["choices"][0]["message"]
    print(f"   响应: {msg.get('content')}")
    
    # 2. 测试通过我们的代码逻辑提取
    print()
    print("2. 测试我们的代码逻辑...")
    # 模拟一下message对象
    class MockMessage:
        def __init__(self, content, reasoning_content=None, model_extra=None):
            self.content = content
            self.reasoning_content = reasoning_content
            self.model_extra = model_extra or {}
    msg_obj = MockMessage(
        content=msg.get('content'),
        reasoning_content=msg.get('reasoning_content')
    )
    print(f"   模拟Message对象")
    
    # 复制我们的提取逻辑
    content_candidate = None
    if hasattr(msg_obj, 'content') and msg_obj.content:
        content_candidate = msg_obj.content.strip()
    if not content_candidate and hasattr(msg_obj, 'reasoning_content') and msg_obj.reasoning_content:
        content_candidate = msg_obj.reasoning_content.strip()
    if not content_candidate and hasattr(msg_obj, 'model_extra') and 'reasoning_content' in msg_obj.model_extra:
        content_candidate = msg_obj.model_extra['reasoning_content'].strip()
    print(f"   提取结果: {content_candidate}")
    
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("测试完成！")
print("=" * 60)
