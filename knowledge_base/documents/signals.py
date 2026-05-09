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
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE documents_document
            SET search_vector = to_tsvector('chinese', COALESCE(title, '') || ' ' || COALESCE(content, ''))
            WHERE id = %s
        """, [document_id])


def delete_search_vector(document_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE documents_document
            SET search_vector = NULL
            WHERE id = %s
        """, [document_id])


def create_chunks_with_embedding(document):
    from documents.models import DocumentChunk
    
    DocumentChunk.objects.filter(document=document).delete()
    
    text = clean_markdown(document.content or '')
    if not text.strip():
        return
    
    chunks = split_text(text, CHUNK_SIZE, OVERLAP_SIZE)
    
    ai_config = get_ai_config()
    if not ai_config:
        print("AI config not found, skipping embedding generation")
        for i, chunk_content in enumerate(chunks):
            DocumentChunk.objects.create(
                document=document,
                content=chunk_content,
                embedding=None,
                chunk_index=i,
                chunk_size=CHUNK_SIZE,
                overlap_size=OVERLAP_SIZE
            )
        return
    
    for i, chunk_content in enumerate(chunks):
        input_type = ai_config.get('input_type', 'query')
        if input_type == 'document':
            input_type = 'passage'
        embedding = get_embedding(chunk_content, ai_config['api_key'], ai_config['base_url'], ai_config['model_name'], input_type)
        embedding_json = json.dumps(embedding) if embedding else None
        
        DocumentChunk.objects.create(
            document=document,
            content=chunk_content,
            embedding=embedding_json,
            chunk_index=i,
            chunk_size=CHUNK_SIZE,
            overlap_size=OVERLAP_SIZE
        )


def delete_chunks(document_id):
    DocumentChunk.objects.filter(document_id=document_id).delete()


@receiver(post_save, sender=Document)
def handle_document_save(sender, instance, created, **kwargs):
    if instance.publish_status == 'published':
        update_search_vector(instance.id)
        create_chunks_with_embedding(instance)
    else:
        delete_search_vector(instance.id)
        delete_chunks(instance.id)


@receiver(post_delete, sender=Document)
def handle_document_delete(sender, instance, **kwargs):
    delete_search_vector(instance.id)
    delete_chunks(instance.id)