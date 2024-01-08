from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Member

# 사용자의 입력 처리를 위한 시리얼라이저
class MemberRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['email', 'password', 'nickname']

    # 비밀번호 해싱처리
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)