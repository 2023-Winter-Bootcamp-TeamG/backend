from django.urls import path
from .views import PhotoManageView
from .views import PhotoDetailView

urlpatterns = [
    # 사진 저장/전체 불러오기
    path('api/v1/photos/', PhotoManageView.as_view(), name='photo-album'),
    path('api/v1/photos/<int:id>', PhotoDetailView.as_view(), name='photo-detail'),
    ]