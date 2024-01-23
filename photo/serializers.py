from rest_framework import serializers
from .models import Photo
from .models import UsedSticker, TextBox, CustomedPhoto

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['title', 'url']

# 사진 불러오기
class PhotoLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'title', 'url']

#사진 상세보기
class PhotoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'title', 'url', 'created_at']

# 사진 수정
class PhotoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['url']

# qr serializer
class QrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'url']

class UsedStickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedSticker
        fields = ['url', 'x', 'y', 'size']

class TextBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBox
        fields = ['text', 'x', 'y', 'size', 'color', 'font']

class CustomedPhotoSerializer(serializers.ModelSerializer):
    stickers = UsedStickerSerializer(many=True)
    textboxes = TextBoxSerializer(many=True)

    class Meta:
        model = CustomedPhoto
        fields = ['photo_url', 'stickers', 'textboxes']

    def create(self, validated_data):
        stickers_data = validated_data.pop('stickers')
        textboxes_data = validated_data.pop('textboxes')
        customed_photo = CustomedPhoto(**validated_data)
        customed_photo.save(using='mongodb')  # MongoDB를 명시적으로 사용
        for sticker_data in stickers_data:
            UsedSticker.objects.create(customed_photo=customed_photo, **sticker_data, using='mongodb')
        for textbox_data in textboxes_data:
            TextBox.objects.create(customed_photo=customed_photo, **textbox_data, using='mongodb')
        return customed_photo
