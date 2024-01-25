import base64
import io
from .models import Photo, TextBox, UsedSticker, CustomedPhoto
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PhotoSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PhotoLoadSerializer
import os
from .serializers import PhotoUpdateSerializer, PhotoDetailSerializer
from .tasks import save_photo_model, delete_from_s3, update_photo
from django.core.paginator import Paginator, EmptyPage
from PIL import Image
import re
import qrcode
from io import BytesIO
import base64
from .serializers import QrSerializer
from .serializers import CustomedPhotoSerializer

# Create your views here.
# 앨범 관련 뷰
class PhotoManageView(APIView):
    @swagger_auto_schema(
        operation_summary="Upload Photo and Customed Data",
        operation_description="Upload original and customed photos with stickers and textboxes data.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'photo_data': openapi.Schema(type=openapi.TYPE_STRING, description='Base64 encoded photo data'),
                'result_photo_data': openapi.Schema(type=openapi.TYPE_STRING,
                                                    description='Base64 encoded customed photo data'),
                'stickers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, ref='#/definitions/UsedSticker'),
                    description='List of stickers'
                ),
                'textboxes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, ref='#/definitions/TextBox'),
                    description='List of textboxes'
                )
            }
        ),
        responses={202: openapi.Response('Processing started')}
    )

    # 사진을 앨범에 업로드
    def post(self, request, *args, **kwargs):
        if not request.user.id:
            return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        member_id = request.user.id

        photo_data_with_prefix = request.data.get('photo_data')
        result_photo_data_with_prefix = request.data.get('result_photo_data')
        stickers_data = request.data.get('stickers', [])
        textboxes_data = request.data.get('textboxes', [])

        photo_match = re.match(r'data:image/(?P<format>\w+);base64,(?P<data>.+)', photo_data_with_prefix)
        result_photo_match = re.match(r'data:image/(?P<format>\w+);base64,(?P<data>.+)', result_photo_data_with_prefix)

        if (not photo_match) or (not result_photo_match):
            return Response({"error": "Invalid image data format"}, status=status.HTTP_400_BAD_REQUEST)

        photo_format = photo_match.group('format')
        base64_photo = photo_match.group('data')

        result_photo_format = result_photo_match.group('format')
        base64_result_photo = result_photo_match.group('data')

        photo_extension = "." + photo_format.lower()
        result_photo_extension = "." + result_photo_format.lower()

        try:
            photo_data = base64.b64decode(base64_photo)
            result_photo_data = base64.b64decode(base64_result_photo)
        except Exception as e:
            return Response({"error": "Invalid image data: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        save_photo_model.delay(member_id, photo_data, photo_extension, result_photo_data, result_photo_extension, stickers_data, textboxes_data)

        return Response({"message": "Save processing started"}, status=status.HTTP_202_ACCEPTED)

    # # base64 인코딩된 이미지 데이터를 받음
        # base64_image_with_prefix = request.data.get('url') # request의 url을 가져옴
        # image_title = request.data.get('title') # request의 title을 가져옴
        #
        # if not base64_image_with_prefix:
        #     return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # match = re.match(r'data:image/(?P<format>\w+);base64,(?P<data>.+)', base64_image_with_prefix)
        # if not match:
        #     return Response({"error": "Invalid image data format"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # image_format = match.group('format')
        # base64_image = match.group('data')
        #
        # extension = "." + image_format.lower() # 확장자 설정
        #
        # try:
        #     image_data = base64.b64decode(base64_image)
        # except Exception as e:
        #     return Response({"error": "Invalid image data: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        #
        # # S3 업로드 및 Photo 객체 저장 비동기 처리
        # save_photo_model.delay(image_data, image_title, extension, member_id)
        #
        # return Response({"message": "Save processing started"}, status=status.HTTP_202_ACCEPTED)

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

        # 현재 클라이언트의 커스텀 된 사진만 필터링
        photos = Photo.objects.filter(member_id=request.user, is_customed=True)

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

class PhotoEditView(APIView):
    parser_classes = [MultiPartParser, FormParser]
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

    def get(self, request, *args, **kwargs):
        photo_id = kwargs.get('id', None) # url의 id를 가져옴

        try:
            # Photo 객체를 id와 member_id를 기준으로 찾음
            photo = Photo.objects.get(id=photo_id, is_customed=True)

            if photo.member_id != request.user: # 요청을 보낸 사용자가 사진의 주인이 아니면 에러 반환
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Photo.DoesNotExist:
            # 해당 조건을 만족하는 Photo 객체가 없으면 404 에러 반환
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Photo 객체를 직렬화
        serializer = PhotoDetailSerializer(photo)

        # 직렬화된 데이터를 응답으로 반환
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Edit a customed photo",
        operation_description="Upload customed photos with stickers and textboxes data.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result_photo_data': openapi.Schema(type=openapi.TYPE_STRING,
                                                    description='Base64 encoded customed photo data'),
                'stickers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, ref='#/definitions/UsedSticker'),
                    description='List of stickers'
                ),
                'textboxes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, ref='#/definitions/TextBox'),
                    description='List of textboxes'
                )
            }
        ),
        responses={202: openapi.Response('Processing started')}
    )
    def put(self, request, *args, **kwargs):
        photo_id = kwargs.get("id")

        result_photo_data_with_prefix = request.data.get('result_photo_data')
        stickers_data = request.data.get('stickers', [])
        textboxes_data = request.data.get('textboxes', [])
        result_photo_match = re.match(r'data:image/(?P<format>\w+);base64,(?P<data>.+)', result_photo_data_with_prefix)

        if not result_photo_match:
            return Response({"error": "Invalid image data format"}, status=status.HTTP_400_BAD_REQUEST)

        base64_result_photo = result_photo_match.group('data')

        result_photo_data = base64.b64decode(base64_result_photo)

        if not photo_id:
            return Response({"Error": "photo id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            photo = Photo.objects.get(id=photo_id)

            if photo.member_id != request.user:  # 요청을 보낸 사용자가 사진의 주인이 아니면 에러 반환
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

            # 기본 photo 객체의 이미지 파일명 사용
            original_file_name = os.path.basename(photo.url.name)

            # photo 업데이트 비동기처리
            update_photo.delay(photo_id, result_photo_data, original_file_name, stickers_data, textboxes_data)

            return Response({"message": "Update processing started"}, status=status.HTTP_202_ACCEPTED)

        except Photo.DoesNotExist:
            return Response({"Error": "photo not found"}, status=status.HTTP_404_NOT_FOUND)

class QRAPIView(APIView):
    def get(self, request, *args, **kwargs):
        photo_id = kwargs.get("id")

        try:
            photo = Photo.objects.get(id=photo_id)

            if photo.member_id != request.user:
                return Response({"error": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        except Photo.DoesNotExist:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QrSerializer(photo)
        serialized_data = serializer.data
        img = qrcode.make(serialized_data['url'])
        image_io = BytesIO()
        img.save(image_io, format='PNG')
        image_io.seek(0)

        # Encode the image as base64
        image_base64 = base64.b64encode(image_io.getvalue()).decode('utf-8')

        # Include the base64-encoded image in the JSON response
        response_data = {'qr_code': image_base64}

        return Response(response_data, status=status.HTTP_200_OK)
        # return Response({'Message': 'Success'}, status=status.HTTP_200_OK)

class PhotoTestView(APIView):
    @swagger_auto_schema(
        operation_summary="Upload a New Photo",
        operation_description="Upload a new photo with stickers and textboxes.",
        request_body=CustomedPhotoSerializer,
        responses={
            201: CustomedPhotoSerializer(many=False),
            400: 'Bad Request',
            401: 'Unauthorized'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = CustomedPhotoSerializer(data=request.data)
        if serializer.is_valid():
            # 현재 사용자 ID 설정
            serializer.validated_data['user_id'] = request.user.id
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
