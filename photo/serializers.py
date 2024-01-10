from rest_framework import serializers
from .models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'member_id', 'title', 'url', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']