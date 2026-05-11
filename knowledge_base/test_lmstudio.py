#!/usr/bin/env python3
"""测试LM Studio的响应参数"""
import openai
import json

BASE_URL = "http://20.20.100.203:1234/v1"
MODEL_NAME = "qwen3.6-35b-a3b"

print("=" * 60)
print("测试 LM Studio 响应参数")
print("=" * 60)
print()

client = openai.OpenAI(api_key="dummy_key", base_url=BASE_URL)

# 测试1: 正常参数
print("测试1: 正常参数...")
try:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "你好，请用中文回复，简单一点"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    msg = response.choices[0].message
    print(f"  content: {repr(msg.content)}")
    print(f"  reasoning_content: {repr(msg.model_extra.get('reasoning_content', ''))}")
except Exception as e:
    print(f"  错误: {e}")
print()

# 测试2: 尝试禁用推理
print("测试2: 尝试禁用推理...")
try:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "你好，请用中文回复，简单一点"}
        ],
        temperature=0.7,
        max_tokens=100,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}}
    )
    msg = response.choices[0].message
    print(f"  content: {repr(msg.content)}")
    print(f"  reasoning_content: {repr(msg.model_extra.get('reasoning_content', ''))}")
except Exception as e:
    print(f"  错误: {e}")
print()

# 测试3: 从reasoning_content里找最终回复
print("测试3: 解析推理内容...")
if 'msg' in locals():
    reasoning = msg.model_extra.get('reasoning_content', '')
    print(f"  原始推理长度: {len(reasoning)}")
    print()
    print("  " + "="*58)
    if reasoning:
        lines = reasoning.split('\n')
        print(f"  最后5行:")
        for line in lines[-5:]:
            print(f"    {line}")
    print("  " + "="*58)

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
