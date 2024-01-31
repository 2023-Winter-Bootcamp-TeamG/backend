from rest_framework import serializers
from .models import Sticker


class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = ['id', 'member_id', 'image', 'created_at', 'updated_at', 'deleted_at', 'is_ai']
        read_only_fields = ['id', 'member_id', 'created_at', 'updated_at', 'deleted_at', 'is_ai']

class BasicSerializer(serializers.ModelSerializer):
    class meta:
        model = Sticker
        fields = ['id', 'member_id', 'image', 'created_at', 'updated_at', 'deleted_at', 'is_basic']

class AiStickerKeywordRequestSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=True, help_text="Text keyword for the image generation.")


class AiStickerTaskIdRequestSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=True, help_text="task ID for the AI-generated image.")


class AiStickerTaskIdRequestSerializer(serializers.Serializer):
    task_id = serializers.CharField(required=True, help_text="The task ID for the AI-generated image.")
