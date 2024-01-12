from rest_framework import serializers
from photo.models import Photo

# 사용자의 입력 처리를 위한 시리얼라이저
class QrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'url']