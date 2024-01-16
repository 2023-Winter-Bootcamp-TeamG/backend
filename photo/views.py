import uuid
import boto3 # AWS 서비스 지원
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Photo
from .forms import PhotoForm
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PhotoSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PhotoLoadSerializer
import os
from myproject import settings
from .serializers import PhotoUpdateSerializer, PhotoDetailSerializer
from .tasks import save_photo_model, delete_from_s3, update_photo
from django.core.paginator import Paginator, EmptyPage


# swagger 테스트를 위한 일시적으로 csrf 보호 비활성화
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
# 앨범 관련 뷰
@method_decorator(csrf_exempt, name='dispatch')  # swagger 테스트를 위한 일시적으로 csrf 보호 비활성화
class PhotoManageView(APIView):
    parser_classes = [MultiPartParser, FormParser] # 파일과 폼 데이터 처리
    @swagger_auto_schema(
        operation_description="upload a new photo",
        request_body=PhotoSerializer,
        response={202: "Save processing started"}
    )

    # 사진을 앨범에 업로드
    def post(self, request, *args, **kwargs):
        if not request.user.id:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        member_id = request.user.id

        image_file = request.FILES.get('url') # request의 url을 가져옴
        image_title = request.POST.get('title') # request의 title을 가져옴

        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 이미지 파일의 확장자 추출
        extension = os.path.splitext(image_file.name)[1]

        # 이미지를 데이터형식으로 전환
        image_data = image_file.read()

        # S3 업로드 및 Photo 객체 저장 비동기 처리
        save_photo_model.delay(image_data, image_title, extension, member_id)

        return Response({"message": "Save processing started"}, status=status.HTTP_202_ACCEPTED)

    # 앨범에 저장된 전체 사진 보기
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
                default=9
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        if not request.user.id:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        page = request.GET.get('page', 1)
        size = request.GET.get('size', 9)

        try:
            page = int(page)
            size = int(size)
        except ValueError:
            return Response({"error": "Invalid page or size parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # 현재 클라이언트의 사진만 필터링
        photos = Photo.objects.filter(member_id=request.user)

        # Paginator 객체 생성
        paginator = Paginator(photos, size)

        # Paginator를 사용하여 요청된 페이지의 사진 가져오기
        try:
            photos_page = paginator.page(page)
        except EmptyPage:
            return Response({"error": "Page out of range"}, status=status.HTTP_404_NOT_FOUND)

        # Photo 객체를 JSON 형식으로 직렬화
        serializer = PhotoLoadSerializer(photos_page, many=True)

        # 직렬화된 데이터를 응답으로 반환
        return Response(serializer.data)

class PhotoDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Delete a photo by ID",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH,
                description="ID of the photo to delete",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={204: "No Content"}
    )
    def delete(self, request, *args, **kwargs):
        photo_id = kwargs.get("id")

        if not photo_id:
            return Response({"error": "Photo ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            photo = Photo.objects.get(id=photo_id)
            # 현재 클라이언트가 사진의 주인이 아니라면 error 반환
            if photo.member_id != request.user:
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Photo.DoesNotExist:
            return Response({"error": "Photo not found"}, status=status.HTTP_404_NOT_FOUND)

        image_url = photo.url.name  # 이미지 파일의 S3 경로

        # S3에 업로드 되었던 이미지 삭제 비동기 처리
        delete_from_s3.delay(image_url)

        # Photo 모델에서 삭제
        photo.delete()

        return Response({"message": "Delete processing started"}, status=status.HTTP_202_ACCEPTED)


class PhotoDetailView(APIView):
    def get(self, request, *args, **kwargs):
        photo_id = kwargs.get('id', None) # url의 id를 가져옴

        try:
            # Photo 객체를 id와 member_id를 기준으로 찾음
            photo = Photo.objects.get(id=photo_id)

            if photo.member_id != request.user: # 요청을 보낸 사용자가 사진의 주인이 아니면 에러 반환
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Photo.DoesNotExist:
            # 해당 조건을 만족하는 Photo 객체가 없으면 404 에러 반환
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Photo 객체를 직렬화
        serializer = PhotoDetailSerializer(photo)

        # 직렬화된 데이터를 응답으로 반환
        return Response(serializer.data)

class PhotoUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    # 사진 수정
    @swagger_auto_schema(
        operation_description="Update a photo",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH,
                description="id of photo",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        request_body=PhotoUpdateSerializer,
        responses={200: "Success"}
    )
    def patch(self, request, *args, **kwargs):
        image_file=request.FILES.get('url')
        if not image_file:
            return Response({"Error":"photo is not exist"}, status=status.HTTP_400_BAD_REQUEST)

        photo_id=kwargs.get("id")
        if not photo_id:
            return Response({"Error":"photo id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            photo=Photo.objects.get(id=photo_id)

            if photo.member_id != request.user: # 요청을 보낸 사용자가 사진의 주인이 아니면 에러 반환
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

            # 기본 photo 객체의 이미지 파일명 사용
            original_file_name = os.path.basename(photo.url.name)

            image_data = image_file.read()

            # photo 업데이트 비동기처리
            update_photo.delay(photo_id, image_data, original_file_name)

            return Response({"message": "Update processing started"}, status=status.HTTP_202_ACCEPTED)


        except Photo.DoesNotExist:
            return Response({"Error":"photo not found"}, status=status.HTTP_404_NOT_FOUND)
