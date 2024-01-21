# member/urls.py
from django.urls import path
from .views import MemberManageView, LoginAPIView, LogoutAPIView

urlpatterns = [
    # 회원가입 경로
    path('api/v1/auth/member/', MemberManageView.as_view(), name='member manage'),
    # 로그인 경로
    path('api/v1/auth/login/', LoginAPIView.as_view(), name='login'),
    # 로그아웃 경로
    path('api/v1/auth/logout/', LogoutAPIView.as_view(), name='logout'),
]
