#!/usr/bin/env python3
"""测试网络连接"""
import socket
import requests

print("=" * 60)
print("测试网络连接")
print("=" * 60)
print()

IP = "20.20.100.203"

# 1. 测试ping（socket连接）
print(f"1. 测试 TCP 连接 {IP}:80...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((IP, 80))
    if result == 0:
        print("   ✓ 端口80开放")
    else:
        print(f"   ✗ 端口80关闭 (错误代码: {result})")
    sock.close()
except Exception as e:
    print(f"   ✗ 连接失败: {e}")

print()

# 2. 测试其他常见端口
print("2. 测试其他常见端口...")
for port in [80, 443, 8000, 8080,