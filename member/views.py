from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .authentication import MemberAuthenticationBackend
from .serializers import MemberRegistrationSerializer
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated, AllowAny

#회원가입 뷰
class MemberManageView(APIView):
    # 회원가입인 POST형 메소드에 대해서는 인증 절차 적용 안함
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

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

    @swagger_auto_schema(
        operation_description="Delete the authenticated user's account.",
        responses={
            204: 'Successfully deleted',
            403: 'Not authenticated',
        }
    )
    def delete(self, request):
        member = request.user # 요청을 보낸 사용자의 Member 인스턴스
        member.delete()

        return Response({'message': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)

# 로그인 뷰
class LoginAPIView(APIView):
    @swagger_auto_schema(
        operation_description="로그인 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            }
        ),
        responses={200: '로그인 성공', 401: '인증 실패'}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = MemberAuthenticationBackend().authenticate(request, username=email, password=password)
        if user is not None:
            # 여기서 사용자 세션 관리나 토큰 발행 등의 추가적인 작업을 할 수 있습니다.
            return Response({
                'nickname' : user.nickname,
                'message': '로그인 성공!'
            }, status=status.HTTP_200_OK)
        return Response({
            'message': '로그인 실패. 이메일 또는 비밀번호를 확인해주세요.'
        }, status=status.HTTP_401_UNAUTHORIZED)

# 로그아웃 뷰
class LogoutAPIView(APIView):
    @swagger_auto_schema(
        operation_description="로그아웃 API",
        responses={200: '로그아웃 성공'}
    )
    def post(self, request, *args, **kwargs):
        # 사용자 닉네임 가져오기
        user_nickname = None
        if request.user.is_authenticated:
            user_nickname = request.user.nickname
        # 세션을 삭제하여 사용자를 로그아웃 시킴
        request.session.flush()
        return Response({
            'nickname': user_nickname,
            'message': '로그아웃 되었습니다.'
        }, status=status.HTTP_200_OK)