import os
import sys
import django
from celery import Celery

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "woo_me_now_backend.settings.base")
django.setup()

app = Celery('woo_me_now_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
