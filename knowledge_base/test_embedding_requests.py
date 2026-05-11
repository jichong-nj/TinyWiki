#!/usr/bin/env python3
"""
使用 requests 库测试embedding模型配置
配置参数：
- base-url: "http://20.20.100.203:1234/v1"
- api-key: "123"
- model_name: "bge-m3"
"""

import requests
import json


def test_embedding_config():
    """测试embedding模型配置"""
    
    # 配置参数
    config = {
        "base_url": "http://20.20.100.203:1234/v1",
        "api_key": "123",
        "model_name": "bge-m3"
    }
    
    print("=" * 60)
    print("Embedding 模型配置测试 (使用 requests 库)")
    print("=" * 60)
    print(f"Base URL: {config['base_url']}")
    print(f"API Key: {config['api_key']}")
    print(f"Model Name: {config['model_name']}")
    print("=" * 60)
    
    try:
        # 1. 首先测试模型列表
        print("\n1. 测试获取模型列表...")
        models_url = f"{config['base_url'].rstrip('/')}/models"
        response = requests.get(
            models_url,
            headers={"Authorization": f"Bearer {config['api_key']}"},
            timeout=30
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   模型数量: {len(data.get('data', []))}")
            for model in data.get('data', []):
                print(f"   - {model.get('id')}")
        
        print("\n2. 测试 embedding API...")
        embedding_url = f"{config['base_url'].rstrip('/')}/embeddings"
        
        payload = {
            "model": config['model_name'],
            "input": ["What is the capital of France?"]
        }
        
        print(f"   请求URL: {embedding_url}")
        print(f"   请求参数: {json.dumps(payload, indent=4, ensure_ascii=False)}")
        
        response = requests.post(
            embedding_url,
            json=payload,
            headers={"Authorization": f"Bearer {config['api_key']}"},
            timeout=60
        )
        
        print(f"\n   响应状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   响应内容:")
            print(json.dumps(data, indent=4, ensure_ascii=False))
            
            if "data" in data and len(data["data"]) > 0:
                embedding = data["data"][0]["embedding"]
                print("\n" + "=" * 60)
                print("✓ 测试成功！")
                print("=" * 60)
                print(f"Embedding维度: {len(embedding)}")
                print(f"Embedding前5个值: {embedding[:5]}")
                print("=" * 60)
                return True, "测试通过"
        else:
            print(f"\n   错误响应:")
            print(response.text)
            return False, f"HTTP错误: {response.status_code} - {response.text}"
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ 测试失败！")
        print("=" * 60)
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细堆栈跟踪:")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        
        return False, str(e)


if __name__ == "__main__":
    success, message = test_embedding_config()
    import sys
    sys.exit(0 if success else 1)
