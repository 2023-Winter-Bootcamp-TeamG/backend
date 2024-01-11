# myapp/urls.py

from django.urls import path
from .views import StickerManageView

urlpatterns = [
    path('api/v1/stickers/', StickerManageView.as_view(), name='manage sticker'),
]
