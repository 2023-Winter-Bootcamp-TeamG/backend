from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from .models import Member

class MemberAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            member = Member.objects.get(email=username)
            # 비밀번호 검증
            if check_password(password, member.password):
                return member
        except Member.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Member.objects.get(pk=user_id)
        except Member.DoesNotExist:
            return None
