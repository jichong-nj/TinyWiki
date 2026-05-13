import os
from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        from documents.management.commands.run_document_queue_service import start_queue_service
        start_queue_service()
