from django.urls import path
from .views import FrameManageView

urlpatterns = [
    path('api/vi/frames', FrameManageView.as_view(), name='frame'),
]