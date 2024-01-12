from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class MemberManager(BaseUserManager):
    # 사용자 생성 메소드
    def create_user(self, nickname, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email) # 이메일 정규화
        user = self.model(nickname=nickname, email=email, **extra_fields) # 사용자 인스턴스 생성
        user.set_password(password) # 사용자 비밀번호 해시처리
        user.save(using=self._db)
        return user
    # 관리자 사용자 생성 메소드
    def create_superuser(self, nickname, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(nickname, email, password, **extra_fields)

class Member(AbstractUser):
    email = models.EmailField(unique=True) # 이메일 필드 유니크하게
    nickname = models.CharField(max_length=20, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # username 필드를 nullable로 설정 email로 식별하겠다고 해놔서 이렇게 안해주면 migration이 안됨..
    username = models.CharField(max_length=150, null=True)
    objects = MemberManager()

    def __str__(self):
        return self.nickname

    USERNAME_FIELD = 'email' # 이메일 주소로 사용자를 식별
    REQUIRED_FIELDS = ['nickname']
