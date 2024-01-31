from rest_framework import serializers
from .models import Photo
from .models import UsedSticker, TextBox, Drawing, CustomedPhoto
import collections

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

class PathSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=10)
    points = serializers.ListField(child=serializers.FloatField())

    def to_internal_value(self, data):
        command = data[0]
        points = data[1:]
        return {'command': command, 'points': points}

    def to_representation(self, instance):
        # instance는 Path 모델 인스턴스 또는 OrderedDict 객체일 수 있습니다.
        # OrderedDict 객체인 경우, 'command'와 'points' 키를 사용하여 데이터를 추출합니다.
        if isinstance(instance, collections.OrderedDict):
            command = instance.get('command')
            points = instance.get('points', [])
        # Path 모델 인스턴스인 경우, 직접 속성 값을 사용합니다.
        else:
            command = instance.command
            points = instance.points

        # 명령어를 포함한 전체 리스트를 반환합니다.
        return [command] + points


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
    fill = serializers.IntegerField()
    path = PathSerializer(many=True)
    stroke = serializers.CharField(max_length=30)
    strokeLineCap = serializers.CharField(max_length=30)
    strokeWidth = serializers.IntegerField()
    x = serializers.FloatField()
    y = serializers.FloatField()


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

