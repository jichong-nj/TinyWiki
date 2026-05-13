#!/usr/bin/env python3
"""
自动文档发布脚本
每5秒检查并发布一个未发布的文档
"""

import requests
import time
import sys
import json
from typing import Optional, Dict, Any


class AutoPublisher:
    def __init__(self, base_url: str = "http://localhost:80"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token: Optional[str] = None

    def login(self, username: str, password: str) -> bool:
        """登录获取访问令牌"""
        login_url = f"{self.base_url}/api/accounts/login/"
        data = {
            "username": username,
            "password": password
        }

        try:
            response = self.session.post(login_url, json=data)
            response.raise_for_status()

            result = response.json()
            self.access_token = result.get('access')

            if self.access_token:
                # 设置Authorization头
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                print(f"✅ 登录成功，用户: {username}")
                return True
            else:
                print("❌ 登录失败：未获取到访问令牌")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 登录请求失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ 解析登录响应失败: {e}")
            return False

    def get_unpublished_documents(self) -> list:
        """获取所有未发布的文档"""
        # 获取所有文档，然后筛选publish_status='draft'的
        documents_url = f"{self.base_url}/api/documents/"

        try:
            response = self.session.get(documents_url)
            response.raise_for_status()

            documents = response.json()
            # 筛选未发布的文档
            unpublished = [
                doc for doc in documents
                if doc.get('publish_status') == 'draft'
            ]

            print(f"📄 找到 {len(unpublished)} 个未发布的文档")
            return unpublished

        except requests.exceptions.RequestException as e:
            print(f"❌ 获取文档列表失败: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ 解析文档列表响应失败: {e}")
            return []

    def publish_document(self, document_id: int, document_title: str) -> bool:
        """发布指定的文档"""
        publish_url = f"{self.base_url}/api/documents/{document_id}/publish/"

        try:
            response = self.session.post(publish_url)
            response.raise_for_status()

            result = response.json()
            if result.get('publish_status') == 'published':
                print(f"✅ 文档发布成功: {document_title} (ID: {document_id})")
                return True
            else:
                print(f"⚠️ 文档发布响应异常: {document_title} (ID: {document_id})")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ 发布文档失败: {document_title} (ID: {document_id}) - {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ 解析发布响应失败: {document_title} (ID: {document_id}) - {e}")
            return False

    def run(self, username: str, password: str):
        """主运行循环"""
        print("🚀 启动自动文档发布脚本")
        print(f"📡 API地址: {self.base_url}")

        # 登录
        if not self.login(username, password):
            print("❌ 登录失败，退出脚本")
            sys.exit(1)

        published_count = 0

        while True:
            try:
                # 获取未发布的文档
                unpublished_docs = self.get_unpublished_documents()

                if not unpublished_docs:
                    print("🎉 所有文档都已发布完成！")
                    break

                # 取第一个未发布的文档
                doc = unpublished_docs[0]
                doc_id = doc['id']
                doc_title = doc['title']

                print(f"📝 准备发布文档: {doc_title} (ID: {doc_id})")

                # 发布文档
                if self.publish_document(doc_id, doc_title):
                    published_count += 1
                    print(f"📊 已发布文档总数: {published_count}")
                else:
                    print("⚠️ 发布失败，将在下次循环重试")

                # 等待5秒
                print("⏰ 等待5秒...")
                time.sleep(5)

            except KeyboardInterrupt:
                print("\n🛑 用户中断，退出脚本")
                break
            except Exception as e:
                print(f"❌ 运行时错误: {e}")
                print("⏰ 等待5秒后重试...")
                time.sleep(5)

        print(f"🏁 脚本结束，共发布 {published_count} 个文档")


def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python auto_publish.py <用户名> <密码>")
        print("示例: python auto_publish.py admin mypassword")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    # 可以在这里修改API地址
    base_url = "http://localhost:80"  # 根据需要修改

    publisher = AutoPublisher(base_url)
    publisher.run(username, password)


if __name__ == "__main__":
    main()