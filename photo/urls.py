from django.urls import path
from .views import PhotoUploadView

urlpatterns = [
    # 사진 저장/전체 불러오기
    path('api/v1/photos/', PhotoUploadView.as_view(), name='album_photo'),
    ]