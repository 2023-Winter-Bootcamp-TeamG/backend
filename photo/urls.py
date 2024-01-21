from django.urls import path
from .views import PhotoManageView, PhotoEditView
from .views import QRAPIView

urlpatterns = [
    # 사진 저장/전체 불러오기
    path('api/v1/photos/', PhotoManageView.as_view(), name='photo-album'),
    # 사진 수정/삭제/상세보기
    path('api/v1/photos/<int:id>/', PhotoEditView.as_view(), name='photo-edit'),
    # qr 코드
    path('api/v1/photos/qr/<int:id>/', QRAPIView.as_view(), name='get qr code'),

    ]