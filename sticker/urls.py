# myapp/urls.py

from django.urls import path
from .views import StickerManageView, StickerDeleteView, AiStickerView, AiStickerSaveView, AiStickerDeleteView, \
    AiStickerTaskView

urlpatterns = [
    # 스티커 저장, 불러오기 url
    path('api/v1/stickers/', StickerManageView.as_view(), name='manage sticker'),
    # 스티커 삭제 경로
    path('api/v1/stickers/<int:id>/', StickerDeleteView.as_view(), name='sticker-delete'),
    # AI 스티커
    path('api/v1/stickers/ai/', AiStickerView.as_view(), name='ai sticker'),
    path('api/v1/stickers/ai/save', AiStickerSaveView.as_view(), name='save ai sticker'),
    path('api/v1/stickers/ai/<int:id>/', AiStickerDeleteView.as_view(), name='sticker-delete'),

    path('api/v1/stickers/<str:task_id>/', AiStickerTaskView.as_view(), name='ai sticker task')
]
