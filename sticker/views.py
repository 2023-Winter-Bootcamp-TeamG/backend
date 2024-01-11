import boto3
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

class StickerManageView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # 파일과 폼 데이터 처리
    @swagger_auto_schema(
        operation_description="create a new sticker",
        request_body=StickerSerializer,
        responses={201: StickerSerializer}
    )
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image') # request의 image를 가져옴
        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        input_image = image_file.read() # 이미지를 바이트 데이터로 변환
        output_image = remove(input_image) #변환된 바이트 데이터의 배경 제거

        # 원본 파일의 확장자 추출
        extension = os.path.splitext(image_file.name)[1]

        # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
        image_name = f"{uuid.uuid4()}{extension}"

        # S3에 업로드 할 최종 이미지
        output_image_file = ContentFile(output_image, name=image_name)

        # Sticker 인스턴스 생성 및 저장
        sticker = Sticker(member_id = request.user.id, image = output_image_file)
        sticker.save()

        return Response(StickerSerializer(sticker).data, status=status.HTTP_201_CREATED)

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
        # 여기에 사용자 인증 로직 추가해야됨
        sticker_id = kwargs.get("id")
        if not sticker_id:
            return Response({"error": "Sticker ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sticker = Sticker.objects.get(id=sticker_id)
        except Sticker.DoesNotExist:
            return Response({"error": "Sticker not found"}, status=status.HTTP_404_NOT_FOUND)

        # S3에서 스티커 파일 삭제
        s3 = boto3.client('s3')
        image_url = sticker.image.name  # 스티커 파일의 S3 경로
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            s3.delete_object(Bucket=bucket_name, Key=image_url)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Sticker 모델에서 삭제
        sticker.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)