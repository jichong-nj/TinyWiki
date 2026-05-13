from django.core.management.base import BaseCommand
from documents.models import Document
from documents.signals import update_search_vector, create_chunks_with_embedding


class Command(BaseCommand):
    help = 'Process document publish and analysis queues for documents.'

    def handle(self, *args, **options):
        self.stdout.write('Start processing document queue...')

        publish_queue = Document.objects.filter(publish_status='pending').order_by('updated_at')
        if publish_queue.exists():
            self.stdout.write(f'Publishing {publish_queue.count()} documents...')
            for document in publish_queue:
                try:
                    self.stdout.write(f'Publish queue: document {document.id} {document.title}')
                    update_search_vector(document.id)
                    document.publish_status = 'published'
                    document.save(update_fields=['publish_status'])
                    self.stdout.write(self.style.SUCCESS(f'Document {document.id} published successfully.'))
                except Exception as exc:
                    self.stderr.write(self.style.ERROR(f'Failed to publish document {document.id}: {exc}'))

        analysis_queue = Document.objects.filter(publish_status='published', analysis_status='pending').order_by('updated_at')
        if analysis_queue.exists():
            self.stdout.write(f'Analyzing {analysis_queue.count()} documents...')
            for document in analysis_queue:
                try:
                    self.stdout.write(f'Analysis queue: document {document.id} {document.title}')
                    document.analysis_status = 'analyzing'
                    document.save(update_fields=['analysis_status'])
                    create_chunks_with_embedding(document)
                    document.analysis_status = 'completed'
                    document.save(update_fields=['analysis_status'])
                    self.stdout.write(self.style.SUCCESS(f'Document {document.id} analysis completed.'))
                except Exception as exc:
                    document.analysis_status = 'pending'
                    document.save(update_fields=['analysis_status'])
                    self.stderr.write(self.style.ERROR(f'Failed to analyze document {document.id}: {exc}'))

        self.stdout.write(self.style.SUCCESS('Document queue processing finished.'))
