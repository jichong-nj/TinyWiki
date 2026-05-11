#!/usr/bin/env python3
"""测试ZIP导入的转换逻辑"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from documents.storage_service import StorageService
from documents.document_converter import DocumentConverter
from documents.storage_models import FileStorage

print('='*60)
print('测试ZIP导入的转换逻辑')
print('='*60)

# 检查最近上传的文件
print('\n[1] 查找最近的FileStorage记录...')
recent_files = FileStorage.objects.all().order_by('-created_at')[:5]

for file in recent_files:
    print(f'  - ID: {file.id}, 文件名: {file.file_name}, 文档ID: {file.document_id}')

if not recent_files:
    print('  没有找到文件记录')
    sys.exit(1)

# 测试第一个文件
test_file = recent_files[0]
print(f'\n[2] 测试文件 ID={test_file.id}')
print(f'    文件名: {test_file.file_name}')
print(f'    文件路径: {test_file.full_path}')
print(f'    关联文档: {test_file.document_id}')

# 检查文件是否存在
if os.path.exists(test_file.full_path):
    print(f'    文件存在 ✓')
    with open(test_file.full_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f'    文件内容: {content[:100]}{"..." if len(content) > 100 else ""}')
else:
    print(f'    文件不存在 ✗')

# 测试转换
print(f'\n[3] 测试转换...')
result = DocumentConverter.convert(test_file.id)
print(f'    转换结果: {result}')

# 检查文档是否更新
if test_file.document:
    print(f'\n[4] 检查文档...')
    print(f'    文档ID: {test_file.document.id}')
    print(f'    文档标题: {test_file.document.title}')
    print(f'    文档内容长度: {len(test_file.document.content)}')
    if len(test_file.document.content) < 200:
        print(f'    文档内容: {test_file.document.content}')
    else:
        print(f'    文档内容: {test_file.document.content[:200]}...')

print('\n' + '='*60)
print('测试完成')
print('='*60)
