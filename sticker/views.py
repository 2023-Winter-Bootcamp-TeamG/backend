import boto3
import openai
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from .models import Sticker
from .serializers import StickerSerializer
from rembg import remove
import uuid
import os
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from myproject import settings
from .tasks import save_sticker_model, delete_from_s3
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings
from .serializers import AiStickerSerializer

class StickerManageView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # 파일과 폼 데이터 처리
    @swagger_auto_schema(
        operation_description="create a new sticker",
        request_body=StickerSerializer,
        responses={201: StickerSerializer}
    )
    # 사용자가 업로드한 이미지를 배경제거 한 후 S3에 저장
    def post(self, request, *args, **kwargs):
        if not request.user:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        member_id = request.user.id

        image_file = request.FILES.get('image') # request의 image를 가져옴
        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        input_image = image_file.read() # 이미지를 바이트 데이터로 변환

        # 원본 파일의 확장자 추출
        extension = os.path.splitext(image_file.name)[1]

        # sticker S3 업로드 및 모델 저장 비동기처리
        save_sticker_model.delay(input_image, extension, member_id)

        return Response({"message": "Save processing started"}, status=status.HTTP_202_ACCEPTED)

    # 현재 사용자의 모든 스티커 반환
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='page',
                in_=openapi.IN_QUERY,
                description='Page number',
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                name='size',
                in_=openapi.IN_QUERY,
                description='Number of items per page',
                type=openapi.TYPE_INTEGER,
                default=12
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        # 현재 인증된 사용자의 member_id와 일치하는지 확인
        if not request.user:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        page = request.GET.get('page', 1)
        size = request.GET.get('size', 12)

        try:
            page = int(page)
            size = int(size)
        except ValueError:
            return Response({"error": "Invalid page or size parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # 현재 사용자를 외래키로 가지는 Sticker들
        stickers = Sticker.objects.filter(member_id=request.user)

        paginator = Paginator(stickers, size)

        try:
            stickers_page = paginator.page(page)
        except EmptyPage:
            return Response({"error": "Page out of range"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StickerSerializer(stickers_page, many=True)

        return Response(serializer.data)


# 스티커 삭제 뷰
class StickerDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Delete a sticker by ID",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH,
                description="ID of the sticker to delete",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={204: "No Content"}
    )
    def delete(self, request, *args, **kwargs):
        sticker_id = kwargs.get("id")
        if not sticker_id:
            return Response({"error": "Sticker ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sticker = Sticker.objects.get(id=sticker_id)
            if sticker.member_id != request.user:
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Sticker.DoesNotExist:
            return Response({"error": "Sticker not found"}, status=status.HTTP_404_NOT_FOUND)


        image_url = sticker.image.name  # 스티커 파일의 S3 경로

        # S3에서 스티커 파일 삭제 비동기처리
        delete_from_s3.delay(image_url)

        # Sticker 모델에서 삭제
        sticker.delete()

        return Response({"message": "Delete processing started"}, status=status.HTTP_202_ACCEPTED)

# Dall-E 키 설정
openai.api_key = settings.OPENAI_API_KEY

# AI 스티커
class AiStickerView(APIView):
    # AI 스티커 생성
    @swagger_auto_schema(
        operation_description="Generate an image based on the provided prompt",
        request_body=AiStickerSerializer,
        responses={200: AiStickerSerializer}
    )
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'error':'No prompt provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이미지 생성
            response = openai.Image.create(
                prompts="a description of the image you want",
                n=3,
                size="500x500"
            )

            # 생성된 이미지의 URL 추출
            aisticker_urls = [image_info['url'] for image_info in response['data']]
            return Response({'aisticker_urls': aisticker_urls})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)