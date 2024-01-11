from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QrSerializer
from drf_yasg import openapi
from photo.models import Photo
import qrcode
from io import BytesIO
from PIL import Image
import base64
from rest_framework.permissions import IsAuthenticated

class QRAPIView(APIView):

    permission_classes = [IsAuthenticated] #인증된 사용자만 허용

    @swagger_auto_schema(
        operation_description="qr코드 생성 API",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={
        #         'photo_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Photo id'),
        #     }
        # ),
        responses={200: '생성 성공', 404: '사진이 없습니다'}
    )
    def get(self, request, *args, **kwargs):
        # 사용자가 이미 로그인되어 있는지 확인
        if not request.user.is_authenticated:
            return Response({'error': '로그인이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        photo_id = request.GET.get('id')
        print('Photo id is : ', photo_id)
        try:
            photo = Photo.objects.get(id=photo_id)
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
    
