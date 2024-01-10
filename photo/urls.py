from django.urls import path
from .views import PhotoUploadView

urlpatterns = [
    # 회원가입 경로
    path('api/v1/photos/', PhotoUploadView.as_view(), name='save_photo'),
    ]