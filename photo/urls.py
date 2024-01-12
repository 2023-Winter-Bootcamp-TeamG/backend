from django.urls import path
from .views import PhotoManageView, PhotoDetailView, PhotoUpdateView, PhotoDeleteView

urlpatterns = [
    # 사진 저장/삭제/전체 불러오기
    path('api/v1/photos/', PhotoManageView.as_view(), name='photo-album'),
    # 사진 삭제
    path('api/v1/photos/delete/<int:id>/', PhotoDeleteView.as_view(), name='photo-delete'),
    # 사진 수정
    path('api/v1/photos/update/<int:id>', PhotoUpdateView.as_view(), name='photo update'),
    # 사진 상세보기
    path('api/v1/photos/detail/<int:id>', PhotoDetailView.as_view(), name='photo-detail'),

    ]