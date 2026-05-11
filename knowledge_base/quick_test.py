#!/usr/bin/env python3
"""快速测试 - 直接运行"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from documents.models import Document
from documents.storage_models import FileStorage
from documents.document_converter import DocumentConverter

print('查找最近的文档...')
docs = Document.objects.all().order_by('-created_at')[:3]

for doc in docs:
    print(f'\n文档: {doc.id} - {doc.title}')
    print(f'  内容长度: {len(doc.content)}')
    print(f'  内容: {doc.content}')
    
    # 查找关联的文件
    files = FileStorage.objects.filter(document=doc)
    for f in files:
        print(f'  关联文件: {f.id} - {f.file_name}')
        
        # 如果没有内容，尝试重新转换
        if len(doc.content) == 0:
            print(f'  重新转换文件...')
            result = DocumentConverter.convert(f.id)
            print(f'  转换结果: {result}')
            
            # 重新获取文档
            doc.refresh_from_db()
            print(f'  转换后内容长度: {len(doc.content)}')
            print(f'  转换后内容: {doc.content}')

print('\n完成!')
