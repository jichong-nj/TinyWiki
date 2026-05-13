import os
from django.apps import AppConfig


_queue_service_started = False


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        global _queue_service_started
        if _queue_service_started:
            return
        
        # 避免在autoreload等情况下重复启动
        # 检查RUN_MAIN环境变量，这个变量在Django autoreload时会是'false'
        # 我们要确保只启动一次
        run_main = os.environ.get('RUN_MAIN')
        if run_main is None or run_main != 'false':
            from documents.management.commands.run_document_queue_service import start_queue_service
            start_queue_service()
            _queue_service_started = True
