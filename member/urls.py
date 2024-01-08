# member/urls.py
from django.urls import path
from .views import MemberRegistrationAPIView

urlpatterns = [
    path('api/v1/auth/register/', MemberRegistrationAPIView.as_view(), name='register'),
]
