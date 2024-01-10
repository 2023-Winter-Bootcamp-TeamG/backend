from rest_framework import serializers
from .models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'member_id', 'title', 'url', 'created_at', 'updated_at', 'deleted_at']

# 사진 상세보기
class PhotoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['url', 'title']