import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricepulse.settings')

app = Celery('pricepulse')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()