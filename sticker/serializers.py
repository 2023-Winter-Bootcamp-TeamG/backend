from rest_framework import serializers
from .models import Sticker

class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = ['id', 'member_id', 'image', 'created_at', 'updated_at', 'deleted_at', 'is_ai']
        read_only_fields = ['id', 'member_id', 'created_at', 'updated_at', 'deleted_at', 'is_ai']


class AiStickerKeywordRequestSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=True, help_text="Text keyword for the image generation.")