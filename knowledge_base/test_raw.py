#!/usr/bin/env python3
"""测试原始HTTP请求"""
import requests
import json

BASE_URL = "http://20.20.100.203:1234/v1"
MODEL_NAME = "qwen3.6-35b-a3b"

print("=" * 60)
print("测试原始HTTP请求")
print("=" * 60)
print()

# 方法1: 直接放在body里
print("方法1: 直接放在请求体里...")
payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": "你好，请用中文回复，简单一点"}
    ],
    "temperature": 0.7,
    "max_tokens": 100,
    "top_p": 0.95,
    "chat_template_kwargs": {"enable_thinking": False}
}

try:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json=payload,
        timeout=60
    )
    data = response.json()
    print(f"   状态码: {response.status_code}")
    if "choices" in data:
        msg = data["choices"][0]["message"]
        print(f"   content: {repr(msg.get('content', ''))}")
        print(f"   reasoning_content: {repr(msg.get('reasoning_content', ''))}")
except Exception as e:
    print(f"   错误: {e}")
print()

# 方法2: 检查一下实际可用的参数
print("方法2: 检查模型信息...")
try:
    response = requests.get(f"{BASE_URL}/models", timeout=30)
    data = response.json()
    print(f"   状态码: {response.status_code}")
    print(f"   模型数量: {len(data.get('data', []))}")
    if data.get('data'):
        model = data['data'][0]
        print(f"   模型ID: {model.get('id')}")
        print(f"   模型信息: {json.dumps(model, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"   错误: {e}")
print()

print("=" * 60)
print("测试完成")
print("=" * 60)
