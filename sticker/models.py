from django.db import models
from member.models import Member
class Sticker(models.Model):
    # Member 모델의 PK를 참조하는 외래키
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)

    # S3에 저장된 이미지의 URL을 저장하는 필드
    image = models.ImageField(upload_to='stickers/')

    # 생성, 수정, 삭제 날짜 및 시간
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sticker {self.id}"
