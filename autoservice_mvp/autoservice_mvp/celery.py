import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoservice_mvp.settings')

app = Celery('autoservice_mvp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
