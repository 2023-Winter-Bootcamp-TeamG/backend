import os
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from .models import Frame
from .serializers import FrameSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class FrameManageView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # 파일과 폼 데이터 처리

    @swagger_auto_schema(
        operation_description="upload a new frame",
        request_body=FrameSerializer,
        response={202: FrameSerializer}
    )

    def post(self, request, *args, **kwargs):
        grid = request.POST.get('grid') # request에 grid를 가져옴
        image_file = request.FILES.get('image') # request에 image를 가져옴

        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 이미지 파일의 확장자 추출
        extension = os.path.splitext(image_file.name)[1]

        # 이미지를 데이터형식으로 전환
        image_data = image_file.read()

        # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
        image_name = f"{uuid.uuid4()}{extension}"

        result_image_file = ContentFile(image_data, name=image_name)

        frame = Frame(grid=grid, image=result_image_file)

        frame.save()

        return Response({"Successfully uploaded"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'grid', openapi.IN_QUERY,
                description="Grid parameter description",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        grid = request.GET.get('grid', None)

        if grid == None:
            return Response({"error":"grid is not exist"}, status=status.HTTP_400_BAD_REQUEST)

        frames = Frame.objects.filter(grid=grid)

        serializer = FrameSerializer(frames, many=True)

        return Response(serializer.data)