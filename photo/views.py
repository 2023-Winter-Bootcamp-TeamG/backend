from django.shortcuts import render
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

# Create your views here.
# 이미지 업로드 뷰
class PhotoUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser] # 파일과 폼 데이터 처리
    @swagger_auto_schema(
        request_body=PhotoSerializer,
        response={201: PhotoSerializer(many=False)}
    )

    # 사진을 앨범에 업로드
    def post(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# class PhotoListCreateView(generics.ListCreateAPIView):
#     queryset = Photo.objects.all()
#     serializer_class = PhotoSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)