import time
from django.core.management.base import BaseCommand
from django.db import transaction
from documents.models import Document, DocumentChunk
from documents.signals import update_search_vector, create_chunks_with_embedding


class Command(BaseCommand):
    help = 'Process document publish and analysis queues for documents (one-shot).'

    EMBEDDING_RETRY_INTERVAL = 2  # seconds
    EMBEDDING_MAX_RETRIES = 5

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('Start processing document queue (one-shot)...')
        self.stdout.write(f'Chunk retry interval: {self.EMBEDDING_RETRY_INTERVAL} seconds')
        self.stdout.write(f'Chunk max retries: {self.EMBEDDING_MAX_RETRIES}')
        self.stdout.write('=' * 60)

        try:
            self.process_publish_queue()
            self.process_analysis_queue()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Fatal error in queue processing: {e}'))

        self.stdout.write(self.style.SUCCESS('Document queue processing finished.'))

    def process_publish_queue(self):
        """处理发布队列"""
        self.stdout.write('-' * 40)
        self.stdout.write('Processing publish queue...')

        try:
            publish_queue = Document.objects.filter(publish_status='pending').order_by('updated_at')
            queue_count = publish_queue.count()
            self.stdout.write(f'Found {queue_count} documents in publish queue')

            if queue_count == 0:
                self.stdout.write('Publish queue is empty')
                return

            for document in publish_queue:
                self.process_single_publish(document)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error processing publish queue: {e}'))

    def process_single_publish(self, document):
        """处理单个文档的发布"""
        self.stdout.write(f'  [Publish] Document {document.id} "{document.title}"')

        try:
            self.stdout.write(f'    - Calling update_search_vector...')
            update_search_vector(document.id)

            with transaction.atomic():
                document.publish_status = 'published'
                document.save(update_fields=['publish_status'])
                self.stdout.write(self.style.SUCCESS(f'    - Published successfully'))

        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'    - Failed: {exc}'))
            try:
                document.publish_status = 'draft'
                document.save(update_fields=['publish_status'])
                self.stdout.write(f'    - Status reverted to draft')
            except Exception as save_error:
                self.stderr.write(self.style.ERROR(f'    - Failed to revert status: {save_error}'))

    def process_analysis_queue(self):
        """处理分析队列"""
        self.stdout.write('-' * 40)
        self.stdout.write('Processing analysis queue...')

        try:
            analysis_queue = Document.objects.filter(
                publish_status='published',
                analysis_status='pending'
            ).order_by('updated_at')

            queue_count = analysis_queue.count()
            self.stdout.write(f'Found {queue_count} documents in analysis queue')

            if queue_count == 0:
                self.stdout.write('Analysis queue is empty')
                return

            for document in analysis_queue:
                self.process_single_analysis(document)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error processing analysis queue: {e}'))

    def process_single_analysis(self, document):
        """处理单个文档的分析"""
        self.stdout.write(f'  [Analysis] Document {document.id} "{document.title}"')

        try:
            with transaction.atomic():
                document.analysis_status = 'analyzing'
                document.save(update_fields=['analysis_status'])
                self.stdout.write(f'    - Status: analyzing')

            self.stdout.write(f'    - Creating chunks and generating embeddings...')
            create_chunks_with_embedding(document)

            with transaction.atomic():
                document.analysis_status = 'completed'
                document.save(update_fields=['analysis_status'])
                self.stdout.write(self.style.SUCCESS(f'    - Analysis completed successfully'))

        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'    - Failed: {exc}'))
            try:
                with transaction.atomic():
                    document.analysis_status = 'pending'
                    document.save(update_fields=['analysis_status'])
                    self.stdout.write(f'    - Status reverted to pending')
            except Exception as save_error:
                self.stderr.write(self.style.ERROR(f'    - Failed to revert status: {save_error}'))
