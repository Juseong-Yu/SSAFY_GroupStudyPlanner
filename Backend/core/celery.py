from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Redis 등 broker 설정은 settings.py에 CELERY_BROKER_URL 로 분리
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django app 들에서 tasks.py 자동 로드
app.autodiscover_tasks()