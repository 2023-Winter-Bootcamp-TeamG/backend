from __future__ import absolute_import, unicode_literals
from celery import Celery

# Django 프로젝트 설정을 위한 설정
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# 여기서 'myproject'는 당신의 Django 프로젝트 이름입니다.

# Celery 설정을 Django 설정에서 불러오기
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 task를 자동으로 발견하기
app.autodiscover_tasks()
