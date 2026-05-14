#!/usr/bin/env python3
"""Test OpenClaw WebSocket API - Phase 2: Complete handshake"""

import asyncio
import websockets
import json
import uuid
import time
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption


def generate_ed25519_keypair():
    """Generate Ed25519 keypair"""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def derive_device_id(public_key):
    """Derive device ID from public key: SHA-256(raw public key).hex()"""
    raw_public_key = public_key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw
    )
    return hashlib.sha256(raw_public_key).hexdigest()


def encode_public_key(public_key):
    """Encode public key to base64url format"""
    raw_public_key = public_key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw
    )
    # Base64url encode without padding
    b64 = base64.urlsafe_b64encode(raw_public_key).rstrip(b'=').decode('utf-8')
    return b64


def sign_payload(private_key, payload_str):
    """Sign payload string with Ed25519 private key"""
    signature = private_key.sign(payload_str.encode('utf-8'))
    # Base64url encode without padding
    b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode('utf-8')
    return b64


async def test_openclaw_ws():
    """Test OpenClaw WebSocket connection - Phase 2"""
    # Replace with your API URL - convert http to ws
    api_url = "http://localhost:18789"
    ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")
    token = "123ABCdef*"
    
    print(f"Connecting to {ws_url}...")
    
    # Generate keypair
    print("Generating Ed25519 keypair...")
    private_key, public_key = generate_ed25519_keypair()
    device_id = derive_device_id(public_key)
    public_key_b64 = encode_public_key(public_key)
    print(f"Device ID: {device_id}")
    print(f"Public Key: {public_key_b64}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Step 1 & 2: Wait for challenge
            print("Waiting for challenge...")
            challenge_msg = await websocket.recv()
            challenge_data = json.loads(challenge_msg)
            print(f"Challenge received: {json.dumps(challenge_data, indent=2)}")
            
            challenge_nonce = challenge_data["payload"]["nonce"]
            signed_at = int(time.time() * 1000)
            client_id = "cli"
            client_mode = "backend"
            role = "operator"
            scopes = ["operator.admin", "operator.read", "operator.write", "operator.approvals", "operator.pairing"]
            platform = "Linux x86_64"
            
            # Build v2 signature payload (simpler)
            scopes_str = ",".join(scopes)
            payload_str = f"v2|{device_id}|{client_id}|{client_mode}|{role}|{scopes_str}|{signed_at}|{token}|{challenge_nonce}"
            print(f"Signature payload: {payload_str}")
            
            # Sign payload
            signature_b64 = sign_payload(private_key, payload_str)
            print(f"Signature: {signature_b64}")
            
            # Step 3: Send connect handshake
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
                        "instanceId": str(uuid.uuid4())
                    },
                    "role": role,
                    "scopes": scopes,
                    "caps": ["tool-events"],
                    "commands": [],
                    "permissions": {},
                    "auth": {"token": token},
                    "locale": "zh-CN",
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                    "device": {
                        "id": device_id,
                        "publicKey": public_key_b64,
                        "signature": signature_b64,
                        "signedAt": signed_at,
                        "nonce": challenge_nonce
                    }
                }
            }
            
            print(f"Sending connect request: {json.dumps(connect_req, indent=2)}")
            await websocket.send(json.dumps(connect_req))
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if response_data.get("ok"):
                print("\n✅ Handshake successful!")
                
                # First let's get chat history to see the format
                session_key = "jichong"
                agent_id = "main"  # from snapshot.agents[0].agentId
                
                print(f"\n� Getting chat history for agent '{agent_id}', session key '{session_key}'...")
                
                history_req = {
                    "type": "req",
                    "id": str(uuid.uuid4()),
                    "method": "chat.history",
                    "params": {
                        "sessionKey": session_key
                    }
                }
                
                print(f"History request: {json.dumps(history_req, indent=2)}")
                await websocket.send(json.dumps(history_req))
                
                # Wait for history response first
                history_resp = None
                while history_resp is None:
                    msg = await websocket.recv()
                    msg_data = json.loads(msg)
                    print(f"\n📨 Received: {json.dumps(msg_data, indent=2)}")
                    
                    if msg_data.get("type") == "res" and msg_data.get("id") == history_req["id"]:
                        history_resp = msg_data
                        break
                
                # Function to send a message and wait for response
                async def send_message_and_wait(msg_text):
                    print(f"\n💬 Sending '{msg_text}' to session '{session_key}'...")
                    
                    send_req = {
                        "type": "req",
                        "id": str(uuid.uuid4()),
                        "method": "chat.send",
                        "params": {
                            "sessionKey": session_key,
                            "idempotencyKey": str(uuid.uuid4()),
                            "message": msg_text
                        }
                    }
                    
                    await websocket.send(json.dumps(send_req))
                    
                    print("\n📡 Listening for chat responses (timeout in 120 seconds)...")
                    start_time = time.time()
                    full_content = ""
                    while time.time() - start_time < 120:
                        try:
                            msg = await asyncio.wait_for(websocket.recv(), timeout=1)
                            msg_data = json.loads(msg)
                            print(f"\n📨 Received: {json.dumps(msg_data, indent=2)}")
                            
                            # Check if this is a chat message
                            if msg_data.get("type") == "event" and msg_data.get("event") == "chat":
                                payload = msg_data.get("payload", {})
                                message = payload.get("message", {})
                                
                                # Try to get content from message
                                content_blocks = message.get("content", [])
                                temp_content = ""
                                for block in content_blocks:
                                    if block.get("type") == "text":
                                        temp_content = block.get("text", "")
                                
                                # Update full_content if we have something
                                if temp_content:
                                    full_content = temp_content
                                
                                # Check if this is the final state
                                if payload.get("state") == "final" and full_content:
                                    print(f"\n✅ Conversation completed!")
                                    print(f"\n💬 Assistant: {full_content}")
                                    return full_content
                                
                        except asyncio.TimeoutError:
                            continue
                                
                    # If we have partial content, return it
                    if full_content:
                        print(f"\n✅ Conversation completed (timeout)!")
                        print(f"\n💬 Assistant: {full_content}")
                        return full_content
                    return ""
                
                # First round: 你好，你是谁
                await send_message_and_wait("你好，你是谁")
                
                # Second round: 我想写首诗
                await send_message_and_wait("我想写首诗")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_openclaw_ws())
