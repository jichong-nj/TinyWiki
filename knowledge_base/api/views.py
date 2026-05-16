from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import base64
from .models import AIConfig

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
            "language": "zh-CN",
            "openclaw_api_url": "",
            "openclaw_gateway_token": ""
        }
        with open(SYSTEM_CONFIG_FILE, 'w') as f:
            json.dump(default_system_config, f, indent=2)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def ai_config(request):
    """Get or save AI configuration"""
    if request.method == 'GET':
        try:
            # Try to get from database first
            config = AIConfig.objects.first()
            if config:
                return JsonResponse({
                    'success': True,
                    'data': config.to_dict()
                })
            
            # Fallback to file if no database record
            init_config_dir()
            if os.path.exists(AI_CONFIG_FILE):
                with open(AI_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                return JsonResponse({
                    'success': True,
                    'data': data
                })
            
            # Return default
            return JsonResponse({
                'success': True,
                'data': {
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
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取配置失败: {str(e)}'
            })
    else:  # POST
        try:
            init_config_dir()
            data = json.loads(request.body.decode('utf-8'))
            
            # Save to database
            config = AIConfig.from_dict(data)
            config.save()
            
            # Also save to file for backward compatibility
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
                'encoding_format': "float",
                'timeout': 60.0
            }
            
            if input_type:
                embedding_params['extra_body'] = {"input_type": input_type}
                print(f"[DEBUG] test_model - Adding input_type to extra_body: {input_type}")
            
            try:
                response = client.embeddings.create(**embedding_params)
                embedding = response.data[0].embedding
                print(f"[DEBUG] test_model - Embedding dimension: {len(embedding)}")
            except Exception as e:
                print(f"[DEBUG] test_model - First attempt failed: {str(e)}")
                if 'extra_body' not in embedding_params:
                    print(f"[DEBUG] test_model - Trying with extra_body={{input_type: query}}")
                    embedding_params['extra_body'] = {"input_type": "query"}
                    response = client.embeddings.create(**embedding_params)
                    embedding = response.data[0].embedding
                    print(f"[DEBUG] test_model - Embedding dimension (with extra_body): {len(embedding)}")
                elif 'truncate' not in embedding_params['extra_body']:
                    print(f"[DEBUG] test_model - Trying with extra_body={{truncate: NONE}}")
                    embedding_params['extra_body'] = {"truncate": "NONE"}
                    response = client.embeddings.create(**embedding_params)
                    embedding = response.data[0].embedding
                    print(f"[DEBUG] test_model - Embedding dimension (with truncate): {len(embedding)}")
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
@require_http_methods(["GET", "POST"])
def system_config(request):
    """Get or save system configuration"""
    if request.method == 'GET':
        try:
            init_config_dir()
            if os.path.exists(SYSTEM_CONFIG_FILE):
                with open(SYSTEM_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                return JsonResponse({
                    'success': True,
                    'data': data
                })
            return JsonResponse({
                'success': True,
                'data': {
                    "name": "知识库管理系统",
                    "description": "企业级知识库管理系统",
                    "language": "zh-CN"
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取配置失败: {str(e)}'
            })
    else:  # POST
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


# ========== OpenClaw 相关接口 ==========
import asyncio
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from documents.models import KnowledgeBase, Directory, Document, DocumentVersion
from .openclaw_client import OpenClawClient
import os


def get_system_config():
    """获取系统配置"""
    init_config_dir()
    if os.path.exists(SYSTEM_CONFIG_FILE):
        with open(SYSTEM_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"openclaw_api_url": "", "openclaw_gateway_token": ""}


class OpenClawAgentsView(APIView):
    """获取 OpenClaw Agent 列表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            config = get_system_config()
            api_url = config.get('openclaw_api_url', '')
            gateway_token = config.get('openclaw_gateway_token', '')
            
            if not api_url:
                return Response({'success': False, 'message': 'OpenClaw API 地址未配置'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not gateway_token:
                return Response({'success': False, 'message': 'OpenClaw Gateway Token 未配置'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建客户端
            keypair_file = os.path.join(os.path.dirname(__file__), '..', 'openclaw_keypair.pem')
            client = OpenClawClient(
                api_url=api_url,
                token=gateway_token,
                keypair_file=keypair_file
            )
            
            # 获取 Agent 列表
            agents_data = asyncio.run(client.list_agents())
            
            # 格式化响应
            agents = []
            for agent in agents_data:
                agent_id = agent.get('id', '')
                identity = agent.get('identity') or {}
                agents.append({
                    'id': agent_id,
                    'name': agent.get('name', agent_id),
                    'description': agent.get('description', ''),
                    'emoji': identity.get('emoji', '🤖'),
                    'display_name': identity.get('name') or agent.get('name', agent_id),
                    'theme': identity.get('theme', '')
                })
            
            return Response({'success': True, 'data': agents})
        except Exception as e:
            print(f"[ERROR] OpenClawAgentsView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'message': f'获取 Agent 列表失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OpenClawChatView(APIView):
    """与 OpenClaw Agent 对话"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def _parse_attachments(self, request):
        attachments = []
        uploaded_files = request.FILES.getlist('attachments') or request.FILES.getlist('files')
        for uploaded_file in uploaded_files:
            content = uploaded_file.read()
            mime_type = uploaded_file.content_type or 'application/octet-stream'
            encoded = base64.b64encode(content).decode('utf-8')
            if mime_type.startswith('image/'):
                attachments.append({
                    'name': uploaded_file.name,
                    'mimeType': mime_type,
                    'media': f'data:{mime_type};base64,{encoded}'
                })
            else:
                attachments.append({
                    'type': 'file',
                    'mimeType': mime_type,
                    'fileName': uploaded_file.name,
                    'content': encoded
                })

        # 兼容直接传入 attachments JSON 字段的情况
        if not attachments and isinstance(request.data.get('attachments'), list):
            attachments = request.data.get('attachments')
        return attachments
    
    def post(self, request):
        try:
            config = get_system_config()
            api_url = config.get('openclaw_api_url', '')
            gateway_token = config.get('openclaw_gateway_token', '')
            
            if not api_url:
                return Response({'success': False, 'message': 'OpenClaw API 地址未配置'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not gateway_token:
                return Response({'success': False, 'message': 'OpenClaw Gateway Token 未配置'}, status=status.HTTP_400_BAD_REQUEST)
            
            agent_id = request.data.get('agent_id')
            user_query = request.data.get('query', '')
            knowledge_base_id = request.data.get('knowledge_base_id')
            attachments = self._parse_attachments(request)
            
            if not agent_id or (not user_query and not attachments):
                return Response({'success': False, 'message': '缺少必要参数: agent_id 和 query，或至少上传一个附件'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user_query and attachments:
                user_query = '请分析上传的附件并给出结论。'
            
            # 构建知识库上下文
            context = ""
            if knowledge_base_id:
                try:
                    # 获取知识库
                    kb = KnowledgeBase.objects.get(id=knowledge_base_id)
                    
                    # 获取知识库下的文档
                    documents = Document.objects.filter(directory__knowledge_base=kb)
                    
                    context += f"【知识库: {kb.name}】\n"
                    
                    for doc in documents[:20]:  # 最多取20个文档，避免上下文过长
                        # 获取最新版本
                        latest_version = doc.get_current_version()
                        if latest_version:
                            context += f"\n--- 文档: {doc.title} ---\n"
                            content = latest_version.content
                            # 截取文档内容，避免过长
                            if len(content) > 2000:
                                content = content[:2000] + "...[内容已截断]"
                            context += content + "\n"
                except KnowledgeBase.DoesNotExist:
                    pass
            
            # 构建完整的用户消息
            full_user_message = user_query
            if context:
                full_user_message = f"{context}\n\n用户问题: {user_query}"
            
            # 创建客户端
            keypair_file = os.path.join(os.path.dirname(__file__), '..', 'openclaw_keypair.pem')
            client = OpenClawClient(
                api_url=api_url,
                token=gateway_token,
                keypair_file=keypair_file
            )
            
            # 使用用户名作为会话键，实现会话隔离
            session_key = request.user.username
            
            # 发送消息
            assistant_content = asyncio.run(
                client.chat(
                    message=full_user_message,
                    session_key=session_key,
                    agent_id=agent_id,
                    attachments=attachments
                )
            )
            
            return Response({
                'success': True,
                'data': {
                    'response': assistant_content
                }
            })
        except Exception as e:
            print(f"[ERROR] OpenClawChatView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'message': f'对话失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
