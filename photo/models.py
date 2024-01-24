from django.db import models
from member.models import Member
from django_prometheus.models import ExportModelOperationsMixin
from djongo import models as djongo_models

class Photo(ExportModelOperationsMixin('photo'), models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    is_customed = models.BooleanField(default=False)
    url = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title

############## Models for MongoDB ###############
# 커스텀에 사용된 스티커
class UsedSticker(djongo_models.Model):
    url = djongo_models.URLField()
    x = djongo_models.FloatField()
    y = djongo_models.FloatField()
    size = djongo_models.IntegerField()

    # 추상 모델 지정
    class Meta:
        abstract = True
        managed = False

# 커스텀에 사용된 텍스트박스
class TextBox(djongo_models.Model):
    text = djongo_models.TextField()
    x = djongo_models.FloatField()
    y = djongo_models.FloatField()
    size = djongo_models.IntegerField()
    color = djongo_models.CharField(max_length=30)
    font = djongo_models.CharField(max_length=30)

    #추상 모델 지정
    class Meta:
        abstract = True
        managed = False

# 커스텀 된 사진
class CustomedPhoto(djongo_models.Model):
    user_id = djongo_models.IntegerField()
    photo_id = djongo_models.IntegerField()
    photo_url = djongo_models.URLField()
    stickers = djongo_models.ArrayField(model_container=UsedSticker)
    textboxes = djongo_models.ArrayField(model_container=TextBox)

    class Meta:
        managed = False

    def __str__(self):
        return self.photo_url
