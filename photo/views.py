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
    def post(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PhotoListCreateView(generics.ListCreateAPIView):
#     queryset = Photo.objects.all()
#     serializer_class = PhotoSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)