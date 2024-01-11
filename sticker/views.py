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

class StickerManageView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # 파일과 폼 데이터 처리
    @swagger_auto_schema(
        operation_description="create a new sticker",
        request_body=StickerSerializer,
        responses={201: StickerSerializer}
    )
    # 사용자가 업로드한 이미지를 배경제거 한 후 S3에 저장
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

    @swagger_auto_schema(
        operation_description="Retrieve all stickers for the current authenticated user",
        responses={
            200: StickerSerializer(many=True),
            401: 'Unauthorized - User not authenticated'
        }
    )
    # 현재 사용자의 모든 스티커 반환
    def get(self, request, *args, **kwargs):
        # 현재 인증된 사용자의 member_id와 일치하는지 확인
        if request.user.is_authenticated:
            member_id = request.user.id # 현재 사용자의 id 저장
            stickers = Sticker.objects.filter(member_id=member_id) # 현재 사용자의 id를 외래키로 가지는 Sticker들
            serializer = StickerSerializer(stickers, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

