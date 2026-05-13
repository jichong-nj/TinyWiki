import os
from django.apps import AppConfig


_queue_service_started = False


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # 移除自动启动 queue service 的代码
        # 现在需要手动运行 `python manage.py run_document_queue_service` 来启动
        pass
