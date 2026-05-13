import time
import logging
import threading
from django.db import transaction
from documents.models import Document, DocumentChunk
from documents.signals import update_search_vector, create_chunks_with_embedding

logger = logging.getLogger(__name__)

PUBLISH_PROCESS_INTERVAL = 2  # 发布处理间隔（秒）
ANALYSIS_PROCESS_INTERVAL = 2  # 分析处理间隔（秒）

_service_started = False
_service_lock = threading.Lock()


def start_queue_service():
    """启动队列服务（模块级函数，可直接导入调用）"""
    global _service_started
    with _service_lock:
        if _service_started:
            logger.info('Queue service already started, skipping...')
            return
        _service_started = True

    print('=' * 60)
    print('Document Queue Background Service Started')
    print(f'Publish process interval: {PUBLISH_PROCESS_INTERVAL} seconds')
    print(f'Analysis process interval: {ANALYSIS_PROCESS_INTERVAL} seconds')
    print('=' * 60)

    publish_thread = None
    analysis_thread = None

    try:
        publish_thread = threading.Thread(target=publish_worker, daemon=True, name='Publish-Queue-Worker')
        analysis_thread = threading.Thread(target=analysis_worker, daemon=True, name='Analysis-Queue-Worker')

        publish_thread.start()
        logger.info('Publish queue worker thread started')
        print('Publish queue worker started')

        analysis_thread.start()
        logger.info('Analysis queue worker thread started')
        print('Analysis queue worker started')

        def monitor_threads():
            nonlocal publish_thread, analysis_thread
            while True:
                if not publish_thread.is_alive():
                    logger.error('Publish thread died, restarting...')
                    print('ERROR: Publish thread died, restarting...')
                    publish_thread = threading.Thread(target=publish_worker, daemon=True, name='Publish-Queue-Worker')
                    publish_thread.start()

                if not analysis_thread.is_alive():
                    logger.error('Analysis thread died, restarting...')
                    print('ERROR: Analysis thread died, restarting...')
                    analysis_thread = threading.Thread(target=analysis_worker, daemon=True, name='Analysis-Queue-Worker')
                    analysis_thread.start()

                time.sleep(1)

        monitor_thread = threading.Thread(target=monitor_threads, daemon=True, name='Queue-Monitor')
        monitor_thread.start()

    except Exception as e:
        logger.exception(f'Fatal error in queue service: {e}')
        print(f'ERROR: {e}')


def publish_worker():
    """发布队列处理线程"""
    thread_name = threading.current_thread().name
    logger.info(f'[{thread_name}] Starting publish worker...')
    print(f'[{thread_name}] Starting publish worker...')

    while True:
        try:
            logger.info(f'[{thread_name}] Checking publish queue...')
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] [{thread_name}] Checking publish queue...')

            publish_queue = Document.objects.filter(publish_status='pending').order_by('updated_at')
            queue_count = publish_queue.count()

            if queue_count == 0:
                logger.info(f'[{thread_name}] Publish queue is empty, waiting...')
                print(f'[{thread_name}] Publish queue is empty')
            else:
                logger.info(f'[{thread_name}] Found {queue_count} documents, processing one...')
                print(f'[{thread_name}] Found {queue_count} documents, processing one...')
                document = publish_queue.first()
                process_single_publish(document)

        except Exception as e:
            logger.exception(f'[{thread_name}] Error in publish worker: {e}')
            print(f'[{thread_name}] ERROR: {e}')

        logger.info(f'[{thread_name}] Sleeping for {PUBLISH_PROCESS_INTERVAL} seconds...')
        time.sleep(PUBLISH_PROCESS_INTERVAL)


def analysis_worker():
    """分析队列处理线程"""
    thread_name = threading.current_thread().name
    logger.info(f'[{thread_name}] Starting analysis worker...')
    print(f'[{thread_name}] Starting analysis worker...')

    while True:
        try:
            logger.info(f'[{thread_name}] Checking analysis queue...')
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] [{thread_name}] Checking analysis queue...')

            analysis_queue = Document.objects.filter(
                publish_status='published',
                analysis_status='analyzing'
            ).order_by('updated_at')

            queue_count = analysis_queue.count()

            if queue_count == 0:
                logger.info(f'[{thread_name}] Analysis queue is empty, waiting...')
                print(f'[{thread_name}] Analysis queue is empty')
            else:
                logger.info(f'[{thread_name}] Found {queue_count} documents, processing one...')
                print(f'[{thread_name}] Found {queue_count} documents, processing one...')
                document = analysis_queue.first()
                process_single_analysis(document)

        except Exception as e:
            logger.exception(f'[{thread_name}] Error in analysis worker: {e}')
            print(f'[{thread_name}] ERROR: {e}')

        logger.info(f'[{thread_name}] Sleeping for {ANALYSIS_PROCESS_INTERVAL} seconds...')
        time.sleep(ANALYSIS_PROCESS_INTERVAL)


def process_single_publish(document):
    """处理单个文档的发布"""
    thread_name = threading.current_thread().name
    logger.info(f'[{thread_name}] [Publish] Document ID: {document.id}, Title: {document.title}')
    print(f'  [{thread_name}] [Publish] Document {document.id} "{document.title}"')

    try:
        logger.info(f'[{thread_name}] [Publish] Calling update_search_vector for document {document.id}')
        print(f'    - Calling update_search_vector...')

        update_search_vector(document.id)

        with transaction.atomic():
            document.publish_status = 'published'
            document.save(update_fields=['publish_status'])
            logger.info(f'[{thread_name}] [Publish] Document {document.id} status updated to published')
            print(f'    - Published successfully')

    except Exception as exc:
        logger.exception(f'[{thread_name}] [Publish] Failed to publish document {document.id}: {exc}')
        print(f'    - ERROR: {exc}')

        try:
            document.publish_status = 'draft'
            document.save(update_fields=['publish_status'])
            logger.info(f'[{thread_name}] [Publish] Document {document.id} status reverted to draft')
        except Exception as save_error:
            logger.exception(f'[{thread_name}] [Publish] Failed to revert document {document.id} status: {save_error}')


def process_single_analysis(document):
    """处理单个文档的分析"""
    thread_name = threading.current_thread().name
    logger.info(f'[{thread_name}] [Analysis] Document ID: {document.id}, Title: {document.title}')
    print(f'  [{thread_name}] [Analysis] Document {document.id} "{document.title}"')

    try:
        with transaction.atomic():
            document.analysis_status = 'analyzing'
            document.save(update_fields=['analysis_status'])
            logger.info(f'[{thread_name}] [Analysis] Document {document.id} status updated to analyzing')
            print(f'    - Status: analyzing')

        logger.info(f'[{thread_name}] [Analysis] Calling create_chunks_with_embedding for document {document.id}')
        print(f'    - Creating chunks and generating embeddings...')

        create_chunks_with_embedding(document)

        with transaction.atomic():
            document.analysis_status = 'completed'
            document.save(update_fields=['analysis_status'])
            logger.info(f'[{thread_name}] [Analysis] Document {document.id} analysis completed successfully')
            print(f'    - Analysis completed successfully')

    except Exception as exc:
        logger.exception(f'[{thread_name}] [Analysis] Failed to analyze document {document.id}: {exc}')
        print(f'    - ERROR: {exc}')

        try:
            with transaction.atomic():
                document.analysis_status = 'pending'
                document.save(update_fields=['analysis_status'])
                logger.info(f'[{thread_name}] [Analysis] Document {document.id} status reverted to pending')
                print(f'    - Status reverted to pending')
        except Exception as save_error:
            logger.exception(f'[{thread_name}] [Analysis] Failed to revert document {document.id} status: {save_error}')


from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run background service to process document publish and analysis queues.'

    def handle(self, *args, **options):
        start_queue_service()
