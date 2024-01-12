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
from .serializers import PhotoDetailSerializer
import os
from myproject import settings
from .serializers import PhotoUpdateSerializer

# Create your views here.
# 앨범 관련 뷰
class PhotoManageView(APIView):
    parser_classes = [MultiPartParser, FormParser] # 파일과 폼 데이터 처리
    @swagger_auto_schema(
        operation_description="upload a new photo",
        request_body=PhotoSerializer,
        response={201: PhotoSerializer}
    )

    # 사진을 앨범에 업로드
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('url') # request의 url을 가져옴
        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 이미지 파일의 확장자 추출
        extension = os.path.splitext(image_file.name)[1]

        # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
        image_name = f"{uuid.uuid4()}{extension}"

        image_data = image_file.read()

        result_image_file = ContentFile(image_data, name=image_name)

        photo = Photo(member_id = request.user.id, url = result_image_file)
        photo.save()

        return Response(PhotoSerializer(photo).data, status=status.HTTP_201_CREATED)

        # serializer = PhotoSerializer(data=request.data)
        #
        #
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 앨범에 저장된 전체 사진 보기
    def get(self, request, *args, **kwargs):
        # 클라이언트로부터 전달받은 member_id 쿼리 파라미터를 가져옴
        member_id = request.query_params.get('member_id')

        # member_id가 제공되면 해당하는 사진만 필터링
        if member_id is not None:
            photos = Photo.objects.filter(member_id=member_id)
        else:
            # member_id가 제공되지 않으면 모든 사진을 가져옴
            photos = Photo.objects.all()

        # Photo 객체를 JSON 형식으로 직렬화
        serializer = PhotoSerializer(photos, many=True)

        # 직렬화된 데이터를 응답으로 반환
        return Response(serializer.data)

# 사진 삭제 뷰
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
        # 여기에 사용자 인증 로직 추가해야됨
        photo_id = kwargs.get("id")
        if not photo_id:
            return Response({"error": "Photo ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            photo = Photo.objects.get(id=photo_id)
        except Photo.DoesNotExist:
            return Response({"error": "Photo not found"}, status=status.HTTP_404_NOT_FOUND)

        # S3에서 이미지 파일 삭제
        s3 = boto3.client('s3')
        image_url = photo.url.name  # 이미지 파일의 S3 경로
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            s3.delete_object(Bucket=bucket_name, Key=image_url)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Photo 모델에서 삭제
        photo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PhotoDetailView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'member_id', openapi.IN_QUERY,
                description="Member's ID",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: PhotoDetailSerializer(many=False)}
    )
    def get(self, request, id, *args, **kwargs):
        # URL 경로에서 photo_id와 쿼리 파라미터에서 member_id 가져오기
        member_id = request.query_params.get('member_id')

        try:
            # Photo 객체를 id와 member_id를 기준으로 찾음
            photo = Photo.objects.get(id=id, member_id=member_id)
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

            # 기본 photo 객체의 이미지 파일명 사용
            original_file_name = os.path.basename(photo.url.name)

            image_data = image_file.read()
            result_image_file = ContentFile(image_data, name=original_file_name)

            # 기존 Photo 객체의 url 필드 업데이트
            photo.url = result_image_file
            photo.save()
            return Response({"Message": "Photo updated successfully"}, status=status.HTTP_200_OK)


        except Photo.DoesNotExist:
            return Response({"Error":"photo not found"}, status=status.HTTP_404_NOT_FOUND)
