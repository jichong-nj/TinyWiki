#!/usr/bin/env python3
"""
测试embedding模型配置
配置参数：
- base-url: "http://20.20.100.203:1234/v1"
- api-key: "123"
- model_name: "bge-m3"
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from openai import OpenAI


def test_embedding_config():
    """测试embedding模型配置"""
    
    # 配置参数
    config = {
        "model_type": "embedding",
        "provider": "openai",
        "api_key": "123",
        "base_url": "http://20.20.100.203:1234/v1",
        "model_name": "bge-m3",
        "input_type": "query"
    }
    
    print("=" * 60)
    print("Embedding 模型配置测试")
    print("=" * 60)
    print(f"Base URL: {config['base_url']}")
    print(f"API Key: {config['api_key']}")
    print(f"Model Name: {config['model_name']}")
    print(f"Input Type: {config['input_type']}")
    print("=" * 60)
    
    try:
        # 清理base_url
        base_url = config['base_url'].rstrip('/')
        print(f"\n[DEBUG] 清理后的Base URL: {base_url}")
        
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=config['api_key'],
            base_url=base_url
        )
        
        # 准备embedding参数
        embedding_params = {
            'input': ["What is the capital of France?"],
            'model': config['model_name'],
            'encoding_format': "float",
            'timeout': 60.0
        }
        
        if config.get('input_type'):
            embedding_params['extra_body'] = {"input_type": config['input_type']}
            print(f"[DEBUG] 添加input_type参数到extra_body: {config['input_type']}")
        
        print(f"\n[DEBUG] 开始调用embedding API...")
        print(f"[DEBUG] 请求参数: {embedding_params}")
        
        # 调用embedding API
        response = client.embeddings.create(**embedding_params)
        
        # 获取embedding结果
        embedding = response.data[0].embedding
        
        print("\n" + "=" * 60)
        print("✓ 测试成功！")
        print("=" * 60)
        print(f"Embedding维度: {len(embedding)}")
        print(f"Embedding前5个值: {embedding[:5]}")
        print("=" * 60)
        
        return True, "测试通过"
        
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
    sys.exit(0 if success else 1)
