from django.db import models
from member.models import Member
class Photo(models.Model):
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length = 20, null = False)
    url = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title

# Create your models here.