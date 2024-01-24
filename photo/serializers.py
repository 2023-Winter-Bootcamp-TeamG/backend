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

class UsedStickerSerializer(serializers.Serializer):
    url = serializers.URLField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    size = serializers.IntegerField()

class TextBoxSerializer(serializers.Serializer):
    text = serializers.CharField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    size = serializers.IntegerField()
    color = serializers.CharField(max_length=30)
    font = serializers.CharField(max_length=30)

class CustomedPhotoSerializer(serializers.ModelSerializer):
    stickers = UsedStickerSerializer(many=True)
    textboxes = TextBoxSerializer(many=True)

    class Meta:
        model = CustomedPhoto
        fields = ['photo_url', 'stickers', 'textboxes']

    def create(self, validated_data):
        stickers_data = validated_data.pop('stickers', [])
        textboxes_data = validated_data.pop('textboxes', [])

        # CustomedPhoto 인스턴스 생성
        customed_photo = CustomedPhoto(**validated_data)

        # stickers와 textboxes 필드에 직렬화된 데이터 할당
        customed_photo.stickers = stickers_data
        customed_photo.textboxes = textboxes_data

        customed_photo.save(using='mongodb')
        return customed_photo

