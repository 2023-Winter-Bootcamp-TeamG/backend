from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import MemberRegistrationSerializer

class MemberRegistrationAPIView(APIView):
    @swagger_auto_schema(
        request_body=MemberRegistrationSerializer,
        responses={201: '회원가입 완료', 400: '잘못된 요청'}
    )
    def post(self, request):
        serializer = MemberRegistrationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'nickname': serializer.validated_data.get('nickname'),
                'message': '회원가입 완료.'
            }, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)