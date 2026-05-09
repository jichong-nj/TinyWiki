import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
AI_CONFIG_FILE = os.path.join(CONFIG_DIR, 'ai_config.json')
SYSTEM_CONFIG_FILE = os.path.join(CONFIG_DIR, 'system_config.json')

def init_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    if not os.path.exists(AI_CONFIG_FILE):
        default_ai_config = {
            "textGeneration": {
                "provider": "openai",
                "apiKey": "",
                "baseUrl": "https://api.openai.com/v1",
                "modelName": "gpt-4o",
                "temperature": 0.7
            },
            "embedding": {
                "provider": "openai",
                "apiKey": "",
                "baseUrl": "https://api.openai.com/v1",
                "modelName": "text-embedding-3-large",
                "dimension": 1024
            },
            "rerank": {
                "provider": "cohere",
                "apiKey": "",
                "baseUrl": "https://api.cohere.com/v1",
                "modelName": "rerank-english-v3.0"
            }
        }
        with open(AI_CONFIG_FILE, 'w') as f:
            json.dump(default_ai_config, f, indent=2)
    
    if not os.path.exists(SYSTEM_CONFIG_FILE):
        default_system_config = {
            "name": "知识库管理系统",
            "description": "企业级知识库管理系统",
            "language": "zh-CN"
        }
        with open(SYSTEM_CONFIG_FILE, 'w') as f:
            json.dump(default_system_config, f, indent=2)

@csrf_exempt
@require_http_methods(["POST"])
def test_model(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        model_type = data.get('model_type')
        provider = data.get('provider')
        api_key = data.get('api_key')
        base_url = data.get('base_url')
        model_name = data.get('model_name')
        
        if not all([model_type, provider, api_key, base_url, model_name]):
            return JsonResponse({
                'success': False,
                'message': '缺少必要参数'
            })
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        if model_type == 'textGeneration':
            url = f"{base_url}/chat/completions"
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
        elif model_type == 'embedding':
            url = f"{base_url}/embeddings"
            payload = {
                "model": model_name,
                "input": "Hello"
            }
        elif model_type == 'rerank':
            url = f"{base_url}/rerank"
            payload = {
                "model": model_name,
                "query": "test",
                "documents": ["test document"]
            }
        else:
            return JsonResponse({
                'success': False,
                'message': '未知的模型类型'
            })
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': '测试通过'
            })
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', str(response.status_code))
            except:
                error_message = f'HTTP {response.status_code}'
            
            return JsonResponse({
                'success': False,
                'message': f'测试失败: {error_message}'
            })
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False,
            'message': f'连接失败: {str(e)}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_ai_config(request):
    try:
        init_config_dir()
        data = json.loads(request.body.decode('utf-8'))
        
        with open(AI_CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return JsonResponse({
            'success': True,
            'message': 'AI配置保存成功'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'保存失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_system_config(request):
    try:
        init_config_dir()
        data = json.loads(request.body.decode('utf-8'))
        
        with open(SYSTEM_CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return JsonResponse({
            'success': True,
            'message': '系统配置保存成功'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'保存失败: {str(e)}'
        })