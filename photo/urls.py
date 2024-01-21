from django.urls import path
from .views import PhotoManageView, PhotoDetailView, PhotoUpdateView, PhotoDeleteView
from .views import QRAPIView

urlpatterns = [
    # 사진 저장/삭제/전체 불러오기
    path('api/v1/photos/', PhotoManageView.as_view(), name='photo-album'),
    # 사진 삭제
    path('api/v1/photos/<int:id>/', PhotoDeleteView.as_view(), name='photo-delete'),
    # 사진 수정
    path('api/v1/photos/<int:id>/', PhotoUpdateView.as_view(), name='photo update'),
    # 사진 상세보기
    path('api/v1/photos/<int:id>/', PhotoDetailView.as_view(), name='photo-detail'),
    # qr 코드
    path('api/v1/photos/qr/<int:id>/', QRAPIView.as_view(), name='get qr code'),

    ]