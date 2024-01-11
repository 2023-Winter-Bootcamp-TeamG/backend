# myapp/urls.py

from django.urls import path
from .views import StickerManageView, StickerDeleteView

urlpatterns = [
    # 스티커 저장, 불러오기 url
    path('api/v1/stickers/', StickerManageView.as_view(), name='manage sticker'),
    # 스티커 삭제 경로
    path('api/v1/stickers/delete/<int:id>/', StickerDeleteView.as_view(), name='sticker-delete'),
]
