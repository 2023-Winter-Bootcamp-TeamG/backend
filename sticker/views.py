import base64
import boto3
import openai
from drf_yasg.utils import swagger_auto_schema
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from .models import Sticker
from .serializers import StickerSerializer, AiStickerKeywordRequestSerializer, AiStickerTaskIdRequestSerializer
from rembg import remove
import uuid
import os
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from myproject.settings import AI_STICKER_KEY
from .tasks import save_sticker_model, delete_from_s3, aisticker_create, save_aisticker_model
from django.core.paginator import Paginator, EmptyPage
import requests
from PIL import Image
from io import BytesIO
from celery.result import AsyncResult
from myproject.celery import app
import re


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
        save_sticker_model.delay(input_image, extension, member_id, is_ai=False)

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
        stickers = Sticker.objects.filter(member_id=request.user, is_ai=False)

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
            sticker = Sticker.objects.get(id=sticker_id, is_ai=False)
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


# AI 스티커

class AiStickerView(APIView):
    # AI 스티커 생성
    @swagger_auto_schema(
        request_body=AiStickerKeywordRequestSerializer
    )
    def post(self, request, *args, **kwargs):
        if not request.user:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        keyword = request.data.get('keyword')

        if not keyword:
            return Response({'error': 'No keyword provided'}, status=status.HTTP_400_BAD_REQUEST)

        task = aisticker_create.delay(keyword)

        return Response({"message": "Ai Sticker is created", "task_id": task.id})

    # 현재 사용자의 모든 AI 스티커 반환
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
        stickers = Sticker.objects.filter(member_id=request.user, is_ai=True)

        paginator = Paginator(stickers, size)

        try:
            stickers_page = paginator.page(page)
        except EmptyPage:
            return Response({"error": "Page out of range"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StickerSerializer(stickers_page, many=True)

        return Response(serializer.data)


# AI 스티커 저장
class AiStickerSaveView(APIView):
    @swagger_auto_schema(
        request_body=AiStickerTaskIdRequestSerializer,
        responses={201: StickerSerializer}
    )
    def post(self, request, *args, **kwargs):
        if not request.user:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AiStickerTaskIdRequestSerializer(data=request.data)

        if serializer.is_valid():
            task_id = serializer.validated_data['task_id']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = AsyncResult(task_id)

        if not result.ready():
            return Response({'error': 'Task is not completed yet'}, status=status.HTTP_400_BAD_REQUEST)

        if result.failed():
            return Response({'error': 'Task failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Base64 인코딩된 이미지 데이터
        img_str = result.result

        member_id = request.user.id

        save_aisticker_model.delay(img_str, member_id, is_ai=True)

        return Response({"message": "Save processing started"}, status=status.HTTP_202_ACCEPTED)


# 스티커 삭제 뷰
class AiStickerDeleteView(APIView):
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
            sticker = Sticker.objects.get(id=sticker_id, is_ai=True)
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


# 태스크 상태 조회
class AiStickerTaskView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        if not request.user:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        result = AsyncResult(task_id, app=app)
        response_data = {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None
        }
        return Response(response_data)
