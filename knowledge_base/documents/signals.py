from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import connection
import json

from .models import Document, DocumentChunk
from .embedding import split_text, clean_markdown, get_embedding
from api.models import AIConfig


CHUNK_SIZE = 500
OVERLAP_SIZE = 100


def get_ai_config():
    try:
        config = AIConfig.objects.first()
        if config and config.embedding_api_key and config.embedding_base_url and config.embedding_model_name:
            return {
                'api_key': config.embedding_api_key,
                'base_url': config.embedding_base_url,
                'model_name': config.embedding_model_name,
                'input_type': getattr(config, 'embedding_input_type', 'query')
            }
    except Exception as e:
        print(f"Error getting AI config: {e}")
    return None


def update_search_vector(document_id):
    """更新全文搜索向量，失败时抛出异常"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE documents_document
                SET search_vector = to_tsvector('chinese', COALESCE(title, '') || ' ' || COALESCE(content, ''))
                WHERE id = %s
            """, [document_id])
        return True
    except Exception as e:
        print(f"Error updating search vector: {e}")
        raise  # 抛出异常以便调用者处理


def delete_search_vector(document_id):
    """删除搜索向量"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE documents_document
                SET search_vector = NULL
                WHERE id = %s
            """, [document_id])
    except Exception as e:
        print(f"Error deleting search vector: {e}")


def create_chunks_with_embedding(document):
    """创建文档块并生成嵌入，失败时抛出异常"""
    from documents.models import DocumentChunk
    
    try:
        DocumentChunk.objects.filter(document=document).delete()
        
        text = clean_markdown(document.content or '')
        if not text.strip():
            return
        
        chunks = split_text(text, CHUNK_SIZE, OVERLAP_SIZE)
        
        ai_config = get_ai_config()
        if not ai_config:
            raise Exception("AI embedding configuration not found. Please configure embedding model in settings.")
        
        for i, chunk_content in enumerate(chunks):
            input_type = ai_config.get('input_type', 'query')
            if input_type == 'document':
                input_type = 'passage'
            embedding = get_embedding(chunk_content, ai_config['api_key'], ai_config['base_url'], ai_config['model_name'], input_type)
            
            if embedding is None:
                raise Exception(f"Failed to generate embedding for chunk {i}")
            
            embedding_json = json.dumps(embedding)
            
            DocumentChunk.objects.create(
                document=document,
                content=chunk_content,
                embedding=embedding_json,
                chunk_index=i,
                chunk_size=CHUNK_SIZE,
                overlap_size=OVERLAP_SIZE
            )
    except Exception as e:
        print(f"Error creating chunks with embedding: {e}")
        # 清理已创建的部分数据
        try:
            DocumentChunk.objects.filter(document=document).delete()
        except:
            pass
        raise  # 重新抛出异常


def delete_chunks(document_id):
    """删除文档块"""
    try:
        DocumentChunk.objects.filter(document_id=document_id).delete()
    except Exception as e:
        print(f"Error deleting chunks: {e}")


def publish_document(document):
    """
    发布文档的同步版本：先验证并生成索引和嵌入，成功后才设置为已发布状态
    
    返回 (success: bool, error_message: str)
    """
    try:
        # 1. 先更新全文搜索向量
        update_search_vector(document.id)
        
        # 2. 生成文档块和嵌入
        create_chunks_with_embedding(document)
        
        # 3. 成功后，设置为已发布状态
        document.publish_status = 'published'
        document.analysis_status = 'completed'
        document.save()
        
        return True, ""
    except Exception as e:
        # 失败时回滚：删除可能已创建的索引和块
        try:
            delete_search_vector(document.id)
            delete_chunks(document.id)
        except:
            pass
        
        error_msg = str(e)
        print(f"Publish failed: {error_msg}")
        return False, error_msg


@receiver(post_save, sender=Document)
def handle_document_save(sender, instance, created, **kwargs):
    """
    信号处理：
    - 当已发布文档的内容更新时，重新生成索引和嵌入
    - 发布逻辑通过 publish_document 函数处理
    """
    # 对于已发布的文档，当内容更新时重新生成索引和嵌入
    if instance.publish_status == 'published' and not kwargs.get('raw', False):
        try:
            update_search_vector(instance.id)
            create_chunks_with_embedding(instance)
            # 更新分析状态
            instance.analysis_status = 'completed'
            # 使用 update 避免再次触发信号
            Document.objects.filter(id=instance.id).update(analysis_status='completed')
        except Exception as e:
            print(f"Error updating published document: {e}")
            # 标记为失败状态
            Document.objects.filter(id=instance.id).update(analysis_status='pending')


@receiver(post_delete, sender=Document)
def handle_document_delete(sender, instance, **kwargs):
    delete_search_vector(instance.id)
    delete_chunks(instance.id)