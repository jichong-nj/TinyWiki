#!/usr/bin/env python3
"""测试修复后的完整流程"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')
django.setup()

from api.models import AIConfig
from documents.models import KnowledgeBase, Document
from documents.bm25 import search_hybrid
from documents.chat_models import ChatSession
from django.contrib.auth import get_user_model
import openai

print("=" * 60)
print("测试修复后的完整流程")
print("=" * 60)
print()

# 1. 测试直接调用
print("1. 测试直接调用...")
try:
    config = AIConfig.objects.first()
    client = openai.OpenAI(
        api_key=config.text_generation_api_key,
        base_url=config.text_generation_base_url
    )
    
    response = client.chat.completions.create(
        model=config.text_generation_model_name,
        messages=[
            {"role": "system", "content": "你是一个专业的知识库助手"},
            {"role": "user", "content": "你好，请用中文简短回复"}
        ],
        temperature=0.7,
        max_tokens=200,
        top_p=0.95,
        timeout=60.0,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}}
    )
    
    msg = response.choices[0].message
    print(f"   ✅ 成功！")
    print(f"   content: {repr(msg.content)}")
    print(f"   response: {msg.content}")
    
except Exception as e:
    print(f"   ❌ 失败: {e}")
    import traceback
    traceback.print_exc()
print()

# 2. 测试混合检索
print("2. 测试混合检索...")
try:
    kb = KnowledgeBase.objects.first()
    results = search_hybrid("人工智能", knowledge_base_id=kb.id, top_k=3)
    print(f"   ✅ 成功！找到 {len(results)} 个结果")
    for r in results[:2]:
        print(f"      - {r[2][:30]}...")
except Exception as e:
    print(f"   ❌ 失败: {e}")
print()

print("=" * 60)
print("测试完成！")
print("=" * 60)
