from celery import Celery

from app.config import settings

celery_app = Celery("stackforge", broker=settings.celery_broker_url)
celery_app.conf.task_track_started = True
