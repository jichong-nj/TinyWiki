#!/usr/bin/env python3
"""清理孤立文档 - 那些没有文件夹关联但应该被删除的文档"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from documents.models import Document, Folder, Directory

print('='*60)
print('清理孤立文档')
print('='*60)

# 查找所有文档
all_docs = Document.objects.all()
print(f'\n总文档数: {all_docs.count()}')

# 查找所有文件夹
all_folders = Folder.objects.all()
print(f'总文件夹数: {all_folders.count()}')

# 查找所有目录
all_dirs = Directory.objects.all()
print(f'总目录数: {all_dirs.count()}')

print('\n' + '='*60)
print('分析文档...')
print('='*60)

# 检查每个文档
docs_to_delete = []
docs_ok = []

for doc in all_docs:
    status = []
    
    # 检查目录是否存在
    if doc.directory_id:
        try:
            Directory.objects.get(id=doc.directory_id)
            status.append('目录正常')
        except Directory.DoesNotExist:
            status.append('目录已删除')
            docs_to_delete.append(doc)
            continue
    
    # 检查文件夹是否存在
    if doc.folder_id:
        try:
            Folder.objects.get(id=doc.folder_id)
            status.append('文件夹正常')
        except Folder.DoesNotExist:
            status.append('文件夹已删除')
            docs_to_delete.append(doc)
            continue
    
    # 如果都有或者都没有，认为正常
    if not status:
        status.append('状态正常')
    
    docs_ok.append(doc)
    print(f'  文档 {doc.id}: {doc.title} - {", ".join(status)}')

print('\n' + '='*60)
print('统计:')
print(f'  正常文档: {len(docs_ok)}')
print(f'  孤立文档: {len(docs_to_delete)}')
print('='*60)

if docs_to_delete:
    print(f'\n将要删除的孤立文档:')
    for doc in docs_to_delete:
        print(f'  - {doc.id}: {doc.title}')
    
    confirm = input(f'\n确认删除这 {len(docs_to_delete)} 个文档? (yes/no): ')
    if confirm.lower() == 'yes':
        # 执行删除
        for doc in docs_to_delete:
            doc.delete()
        print(f'\n成功删除 {len(docs_to_delete)} 个孤立文档!')
    else:
        print('取消删除.')
else:
    print('\n没有需要清理的孤立文档!')

print('\n' + '='*60)
print('完成!')
print('='*60)
