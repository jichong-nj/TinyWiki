from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import connection

from .models import Document


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


@receiver(post_save, sender=Document)
def handle_document_save(sender, instance, created, **kwargs):
    if instance.publish_status == 'published':
        update_search_vector(instance.id)
    else:
        delete_search_vector(instance.id)


@receiver(post_delete, sender=Document)
def handle_document_delete(sender, instance, **kwargs):
    delete_search_vector(instance.id)