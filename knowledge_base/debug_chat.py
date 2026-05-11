#!/usr/bin/env python3
"""调试聊天接口"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')
django.setup()

from api.models import AIConfig
from documents.models import KnowledgeBase
from documents.chat_models import ChatSession, ChatMessage
from django.contrib.auth import get_user_model
import openai

print("=" * 60)
print("调试聊天接口")
print("=" * 60)
print()

# 1. 检查配置
print("1. 检查配置...")
config = AIConfig.objects.first()
print(f"   Base URL: {config.text_generation_base_url}")
print(f"   Model: {config.text_generation_model_name}")
print()

# 2. 测试直接调用模型
print("2. 直接测试模型调用...")
try:
    client = openai.OpenAI(
        api_key=config.text_generation_api_key,
        base_url=config.text_generation_base_url
    )
    
    response = client.chat.completions.create(
        model=config.text_generation_model_name,
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好，测试一下"}
        ],
        temperature=0.7,
        max_tokens=100,
        timeout=60.0
    )
    
    print(f"   ✅ 成功！")
    print(f"   响应: {response.choices[0].message}")
except Exception as e:
    print(f"   ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 3. 检查响应结构
print("3. 检查响应结构...")
if 'response' in locals():
    print(f"   响应类型: {type(response)}")
    print(f"   有 choices: {hasattr(response, 'choices')}")
    if hasattr(response, 'choices'):
        print(f"   Choices 数量: {len(response.choices)}")
        msg = response.choices[0].message
        print(f"   消息对象属性: {dir(msg)}")
        print(f"   message.content: {msg.content}")
        if hasattr(msg, 'model_extra'):
            print(f"   message.model_extra: {msg.model_extra}")

print()
print("=" * 60)
print("调试完成")
print("=" * 60)
