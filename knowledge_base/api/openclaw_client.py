
"""OpenClaw WebSocket 客户端"""
import asyncio
import websockets
import json
import base64
import hashlib
import uuid
import time
import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption


class OpenClawClient:
    """OpenClaw WebSocket 客户端"""
    
    def __init__(self, api_url: str, token: str, keypair_file: str = None):
        """初始化客户端
        
        Args:
            api_url: OpenClaw API 地址
            token: OpenClaw Gateway Token
            keypair_file: 密钥对保存路径（可选）
        """
        self.api_url = api_url
        self.token = token
        self.ws_url = api_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.keypair_file = keypair_file
        self._load_or_generate_keypair()
        
    def _load_or_generate_keypair(self):
        """加载或生成 Ed25519 密钥对"""
        if self.keypair_file and os.path.exists(self.keypair_file):
            try:
                with open(self.keypair_file, 'rb') as f:
                    content = f.read()
                
                private_pem_end = content.find(b'-----END PRIVATE KEY-----') + len(b'-----END PRIVATE KEY-----')
                private_pem = content[:private_pem_end]
                public_pem = content[private_pem_end:].lstrip()
                
                self.private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
                self.public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())
                print(f"[OpenClaw] 加载已存在的密钥对")
            except Exception as e:
                print(f"[OpenClaw] 加载密钥对失败，生成新的: {e}")
                self._generate_new_keypair()
        else:
            self._generate_new_keypair()
    
    def _generate_new_keypair(self):
        """生成新的 Ed25519 密钥对"""
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        if self.keypair_file:
            private_pem = self.private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            public_pem = self.public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(self.keypair_file, 'wb') as f:
                f.write(private_pem + b'\n' + public_pem)
            print(f"[OpenClaw] 生成并保存新的密钥对到 {self.keypair_file}")
    
    @property
    def device_id(self) -> str:
        """获取设备 ID"""
        pub_key_bytes = self.public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw
        )
        return hashlib.sha256(pub_key_bytes).hexdigest()
    
    @property
    def public_key_b64(self) -> str:
        """获取 Base64 编码的公钥"""
        pub_key_bytes = self.public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw
        )
        return base64.b64encode(pub_key_bytes).decode('utf-8')
    
    async def connect_and_handshake(self, websocket):
        """连接并完成握手
        
        Args:
            websocket: WebSocket 连接对象
        """
        # 1. 等待挑战
        challenge_msg = await websocket.recv()
        print(f"[OpenClaw] 收到挑战")
        challenge_data = json.loads(challenge_msg)
        challenge_nonce = challenge_data['payload']['nonce']
        signed_at = int(time.time() * 1000)
        
        # 2. 准备签名数据
        client_id = "cli"
        client_mode = "backend"
        role = "operator"
        scopes = ["operator.admin", "operator.read", "operator.write", "operator.approvals", "operator.pairing"]
        scopes_str = ",".join(scopes)
        platform = "Linux x86_64"
        
        # 构建 payload (v2 格式)
        payload = f"v2|{self.device_id}|{client_id}|{client_mode}|{role}|{scopes_str}|{signed_at}|{self.token}|{challenge_nonce}"
        
        # 签名
        signature = self.private_key.sign(payload.encode('utf-8'))
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # 3. 发送连接请求
        connect_req = {
            "type": "req",
            "id": str(uuid.uuid4()),
            "method": "connect",
            "params": {
                "minProtocol": 3,
                "maxProtocol": 3,
                "client": {
                    "id": client_id,
                    "version": "control-ui",
                    "platform": platform,
                    "mode": client_mode,
                    "instanceId": "test-cli-instance-12345"
                },
                "role": role,
                "scopes": scopes,
                "caps": ["tool-events"],
                "commands": [],
                "permissions": {},
                "auth": {"token": self.token},
                "locale": "zh-CN",
                "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "device": {
                    "id": self.device_id,
                    "publicKey": self.public_key_b64,
                    "signature": signature_b64,
                    "signedAt": signed_at,
                    "nonce": challenge_nonce
                }
            }
        }
        
        print(f"[OpenClaw] 发送连接请求")
        await websocket.send(json.dumps(connect_req))
        
        # 4. 等待响应
        response = await websocket.recv()
        response_data = json.loads(response)
        
        if not response_data.get("ok"):
            error_msg = response_data.get("error", {}).get("message", "未知错误")
            print(f"[OpenClaw] 握手失败: {error_msg}")
            raise Exception(f"握手失败: {error_msg}")
        
        print(f"[OpenClaw] 握手成功")
    
    async def chat(self, message: str, session_key: str = "default", agent_id: str = "main", attachments: list = None):
        """与 OpenClaw Agent 对话
        
        Args:
            message: 用户消息
            session_key: 会话键（用于隔离不同用户的会话）
            agent_id: Agent ID
            attachments: 附件列表（可选）
            
        Returns:
            Agent 回复内容
        """
        if attachments is None:
            attachments = []
        
        print(f"[OpenClaw] 开始连接到 {self.ws_url}")
        async with websockets.connect(self.ws_url) as websocket:
            print(f"[OpenClaw] 连接已建立，开始握手")
            await self.connect_and_handshake(websocket)
            print(f"[OpenClaw] 握手完成")
            
            await asyncio.sleep(0.3)
            
            # 通过 sessionKey 选择 agent，避免 chat.send 根级参数中出现 agentId
            if agent_id:
                if session_key.startswith("agent:"):
                    parts = session_key.split(":")
                    session_key = f"agent:{agent_id}:{':'.join(parts[2:])}"
                else:
                    session_key = f"agent:{agent_id}:{session_key}"

            params = {
                "sessionKey": session_key,
                "idempotencyKey": str(uuid.uuid4()),
                "message": message
            }
            
            if attachments:
                params["attachments"] = attachments
            
            send_req = {
                "type": "req",
                "id": str(uuid.uuid4()),
                "method": "chat.send",
                "params": params
            }
            
            print(f"[OpenClaw] 发送消息到 Agent {agent_id}, 会话 {session_key}")
            await websocket.send(json.dumps(send_req))
            
            # 等待响应
            final_response = ""
            timeout_count = 0
            max_timeout = 5  # 最多等待 5 次超时
            
            while True:
                try:
                    msg_str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    msg = json.loads(msg_str)
                    
                    # 检查响应状态
                    if msg.get("type") == "res" and not msg.get("ok"):
                        error_msg = msg.get("error", {}).get("message", "未知错误")
                        print(f"[OpenClaw] 请求错误: {error_msg}")
                        raise Exception(error_msg)

                    if msg.get("type") == "event":
                        event_name = msg.get("event")
                        payload = msg.get("payload", {})
                        content = ""
                        state = payload.get("state")

                        if event_name in {"chat", "chat.message"}:
                            message = payload.get("message", {})
                            if isinstance(message, dict):
                                blocks = message.get("content", [])
                                if isinstance(blocks, list):
                                    for block in blocks:
                                        if block.get("type") == "text":
                                            content += block.get("text", "")
                                        elif block.get("type") == "markdown":
                                            content += block.get("text", "")
                                if not content:
                                    content = message.get("text", "")

                        elif event_name == "agent":
                            agent_data = payload.get("data", {})
                            if isinstance(agent_data, dict):
                                content = agent_data.get("text", "")
                                if content and not isinstance(content, str):
                                    content = str(content)
                                if not state:
                                    state = payload.get("stream")

                        if content:
                            final_response = content

                        if state == "final" or state == "end":
                            print(f"[OpenClaw] 收到最终响应")
                            break
                        elif state in {"delta", "generating", "assistant", "start", "working"}:
                            print(f"[OpenClaw] Agent 正在生成响应... state={state}")
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"[OpenClaw] 等待响应超时 ({timeout_count}/{max_timeout})")
                    if timeout_count >= max_timeout:
                        raise Exception("等待响应超时，请重试")
                    continue
            
            return final_response
    
    async def list_agents(self):
        """获取可用的 Agent 列表
        
        Returns:
            Agent 列表
        """
        print(f"[OpenClaw] 开始连接以获取 Agent 列表")
        async with websockets.connect(self.ws_url) as websocket:
            print(f"[OpenClaw] 连接已建立，开始握手")
            await self.connect_and_handshake(websocket)
            print(f"[OpenClaw] 握手完成，获取 Agent 列表")
            
            await asyncio.sleep(0.3)
            
            # 支持不同版本 OpenClaw 的 agent 列表方法
            candidate_methods = ["agents.list", "agent.listAgents", "agent.list"]
            response = []
            for method in candidate_methods:
                req_id = str(uuid.uuid4())
                list_req = {
                    "type": "req",
                    "id": req_id,
                    "method": method
                }

                await websocket.send(json.dumps(list_req))
                print(f"[OpenClaw] 发送 Agent 列表请求: {method}")

                timeout_count = 0
                max_timeout = 5
                
                while True:
                    try:
                        msg_str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        msg = json.loads(msg_str)
                        
                        # 检查响应状态
                        if msg.get("type") == "res" and msg.get("id") == req_id:
                            if not msg.get("ok"):
                                error_msg = msg.get("error", {}).get("message", "未知错误")
                                print(f"[OpenClaw] 获取 Agent 列表错误({method}): {error_msg}")
                                if "unknown method" in error_msg.lower():
                                    break
                                raise Exception(error_msg)

                            response = msg.get("payload", {}).get("agents", [])
                            print(f"[OpenClaw] 获取到 {len(response)} 个 Agent")
                            return response
                    except asyncio.TimeoutError:
                        timeout_count += 1
                        print(f"[OpenClaw] 等待 Agent 列表超时 ({timeout_count}/{max_timeout})")
                        if timeout_count >= max_timeout:
                            raise Exception("获取 Agent 列表超时，请重试")
                        continue

            raise Exception("当前 OpenClaw 服务器不支持 agent 列表接口，请检查版本")


def load_file_as_attachment(file_path: str):
    """加载文件为附件格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        附件字典
    """
    import os
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    # 确定 MIME 类型
    mime_type_map = {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    mime_type = mime_type_map.get(ext, "application/octet-stream")
    
    # 读取并编码文件
    with open(file_path, 'rb') as f:
        file_data = f.read()
    b64_data = base64.b64encode(file_data).decode('utf-8')
    
    # 根据类型返回不同格式
    is_image = mime_type.startswith("image/")
    
    if is_image:
        return {
            "name": filename,
            "mimeType": mime_type,
            "media": f"data:{mime_type};base64,{b64_data}"
        }
    else:
        return {
            "type": "file",
            "mimeType": mime_type,
            "fileName": filename,
            "content": b64_data
        }

