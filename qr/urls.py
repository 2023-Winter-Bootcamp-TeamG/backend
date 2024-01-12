# qr/urls.py
from django.urls import path
from .views import QRAPIView

urlpatterns = [
    # qr 생성 경로
    path('api/v1/qr', QRAPIView.as_view(), name='qr'),
]