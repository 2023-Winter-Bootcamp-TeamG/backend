from django.db import models
from member.models import Member
from django_prometheus.models import ExportModelOperationsMixin
from djongo import models as djongo_models

class Photo(ExportModelOperationsMixin('photo'), models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    origin = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='derived_photos')
    is_customed = models.BooleanField(default=False)
    title = models.CharField(max_length=20)
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
    size = djongo_models.JSONField(default=dict)  # JSON 형태로 width와 height 저장

    class Meta:
        managed = False

# 커스텀에 사용된 텍스트박스
class TextBox(djongo_models.Model):
    text = djongo_models.TextField()
    x = djongo_models.FloatField()
    y = djongo_models.FloatField()
    size = djongo_models.JSONField(default=dict)  # JSON 형태로 width와 height 저장
    color = djongo_models.CharField(max_length=30)
    font = djongo_models.CharField(max_length=30)

    class Meta:
        managed = False

# 커스텀에 사용된 드로잉
class Drawing(djongo_models.Model):
    x = djongo_models.FloatField()
    y = djongo_models.FloatField()
    size = djongo_models.IntegerField()
    color = djongo_models.CharField(max_length=30)

    class Meta:
        managed = False

# 커스텀 된 사진
class CustomedPhoto(djongo_models.Model):
    user_id = djongo_models.IntegerField()
    photo_id = djongo_models.IntegerField()
    photo_url = djongo_models.URLField()
    stickers = djongo_models.JSONField()  # UsedSticker 데이터를 JSON 형태로 저장
    textboxes = djongo_models.JSONField()  # TextBox 데이터를 JSON 형태로 저장
    drawings = djongo_models.JSONField() # Drawing 데이터를 JSON 형태로 저장
    class Meta:
        managed = False

    def __str__(self):
        return self.photo_url
