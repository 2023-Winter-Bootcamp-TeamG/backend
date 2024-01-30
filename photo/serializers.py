from rest_framework import serializers
from .models import Photo
from .models import UsedSticker, TextBox, Drawing, CustomedPhoto

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['title', 'url']

# 사진 불러오기
class PhotoLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['origin', 'title', 'url']

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

class SizeSerializer(serializers.Serializer):
    width = serializers.IntegerField()
    height = serializers.IntegerField()

class PositionSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()


class UsedStickerSerializer(serializers.Serializer):
    url = serializers.URLField()
    position = PositionSerializer()
    size = SizeSerializer()

class TextBoxSerializer(serializers.Serializer):
    text = serializers.CharField()
    position = PositionSerializer()
    size = serializers.IntegerField()
    color = serializers.CharField(max_length=30)
    font = serializers.CharField(max_length=30)

class DrawingSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    size = serializers.IntegerField()
    color = serializers.CharField(max_length=30)

class CustomedPhotoSerializer(serializers.ModelSerializer):
    stickers = UsedStickerSerializer(many=True)
    textboxes = TextBoxSerializer(many=True)
    drawings = DrawingSerializer(many=True)

    class Meta:
        model = CustomedPhoto
        fields = ['photo_url', 'stickers', 'textboxes', 'drawings']

    def create(self, validated_data):
        stickers_data = validated_data.pop('stickers', [])
        textboxes_data = validated_data.pop('textboxes', [])
        drawings_data = validated_data.pop('drawings', [])

        # CustomedPhoto 인스턴스 생성
        customed_photo = CustomedPhoto(**validated_data)

        # stickers와 textboxes 필드에 직렬화된 데이터 할당
        customed_photo.stickers = stickers_data
        customed_photo.textboxes = textboxes_data
        customed_photo.drawings = drawings_data

        customed_photo.save(using='mongodb')
        return customed_photo

    def update(self, instance, validated_data):
        # 기존 인스턴스 업데이트 로직
        instance.photo_url = validated_data.get('photo_url', instance.photo_url)
        instance.stickers = validated_data.get('stickers', instance.stickers)
        instance.textboxes = validated_data.get('textboxes', instance.textboxes)
        instance.drawings = validated_data.get('drawings', instance.drawings)
        instance.save(using='mongodb')
        return instance

