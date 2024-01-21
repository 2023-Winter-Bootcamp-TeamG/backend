from django.urls import path
from .views import FrameManageView

urlpatterns = [
    path('api/v1/frames/', FrameManageView.as_view(), name='frame'),
]