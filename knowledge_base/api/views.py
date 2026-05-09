from openai import OpenAI
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
                "dimension": 1024,
                "inputType": "query"
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
        print(f"[DEBUG] test_model called - Method: {request.method}")
        print(f"[DEBUG] test_model called - Body: {request.body.decode('utf-8')}")
        
        data = json.loads(request.body.decode('utf-8'))
        model_type = data.get('model_type')
        provider = data.get('provider')
        api_key = data.get('api_key')
        base_url = data.get('base_url')
        model_name = data.get('model_name')
        input_type = data.get('input_type', 'query')
        
        print(f"[DEBUG] test_model - model_type: {model_type}")
        print(f"[DEBUG] test_model - provider: {provider}")
        print(f"[DEBUG] test_model - base_url: {base_url}")
        print(f"[DEBUG] test_model - model_name: {model_name}")
        print(f"[DEBUG] test_model - input_type: {input_type}")
        
        if not all([model_type, provider, api_key, base_url, model_name]):
            print(f"[ERROR] test_model - Missing parameters")
            return JsonResponse({
                'success': False,
                'message': '缺少必要参数'
            })
        
        base_url = base_url.rstrip('/')
        print(f"[DEBUG] test_model - Cleaned base_url: {base_url}")
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        if model_type == 'textGeneration':
            print(f"[DEBUG] test_model - Testing text generation with {model_name}")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            print(f"[DEBUG] test_model - Response: {response.choices[0].message.content}")
        
        elif model_type == 'embedding':
            print(f"[DEBUG] test_model - Testing embedding with {model_name}")
            print(f"[DEBUG] test_model - Base URL: {base_url}")
            print(f"[DEBUG] test_model - API Key: {api_key[:10]}...")
            
            embedding_params = {
                'input': ["What is the capital of France?"],
                'model': model_name,
                'encoding_format': "float"
            }
            
            if input_type:
                embedding_params['input_type'] = input_type
                print(f"[DEBUG] test_model - Adding input_type: {input_type}")
            
            try:
                response = client.embeddings.create(**embedding_params)
                embedding = response.data[0].embedding
                print(f"[DEBUG] test_model - Embedding dimension: {len(embedding)}")
            except Exception as e:
                print(f"[DEBUG] test_model - First attempt failed: {str(e)}")
                if 'input_type' not in embedding_params:
                    print(f"[DEBUG] test_model - Trying with input_type=query")
                    embedding_params['input_type'] = 'query'
                    response = client.embeddings.create(**embedding_params)
                    embedding = response.data[0].embedding
                    print(f"[DEBUG] test_model - Embedding dimension (with input_type): {len(embedding)}")
                elif 'truncate' not in embedding_params.get('extra_body', {}):
                    print(f"[DEBUG] test_model - Trying with extra_body={{truncate: NONE}}")
                    embedding_params['extra_body'] = {"truncate": "NONE"}
                    response = client.embeddings.create(**embedding_params)
                    embedding = response.data[0].embedding
                    print(f"[DEBUG] test_model - Embedding dimension (with extra_body): {len(embedding)}")
                else:
                    raise
        
        elif model_type == 'rerank':
            print(f"[DEBUG] test_model - Testing rerank with {model_name}")
            response = client.rerank.create(
                model=model_name,
                query="test",
                documents=["test document"]
            )
            print(f"[DEBUG] test_model - Rerank score: {response.results[0].relevance_score}")
        
        else:
            return JsonResponse({
                'success': False,
                'message': '未知的模型类型'
            })
        
        print(f"[DEBUG] test_model - Test passed")
        return JsonResponse({
            'success': True,
            'message': '测试通过'
        })
    
    except Exception as e:
        print(f"[ERROR] test_model - Exception type: {type(e).__name__}")
        print(f"[ERROR] test_model - Exception message: {str(e)}")
        
        import traceback
        traceback.print_exc()
        
        error_message = str(e)
        if '500' in error_message or 'Something went wrong' in error_message:
            error_message = f'服务器错误: {error_message}\n\n可能原因:\n1. 模型暂不可用\n2. API密钥无效或余额不足\n3. 网络连接问题\n4. 请尝试使用其他模型'
        elif 'input_type' in error_message.lower():
            error_message = f'参数错误: 需要 input_type 参数\n\n请在配置中添加 input_type 字段，可选值: query, document'
        
        return JsonResponse({
            'success': False,
            'message': error_message
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
