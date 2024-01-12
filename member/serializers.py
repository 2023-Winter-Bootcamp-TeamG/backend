from rest_framework import serializers
from .models import Member

# 사용자의 입력 처리를 위한 시리얼라이저
class MemberRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['email', 'password', 'nickname']

    def create(self, validated_data):
        user = Member(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user