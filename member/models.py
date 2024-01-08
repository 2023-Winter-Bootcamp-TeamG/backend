from django.db import models

class Member(models.Model):
    id = models.AutoField(primary_key = True) # id값은 자동으로
    nickname = models.CharField(max_length = 20, null = False)
    email = models.EmailField(max_length = 50, null = False, unique = True)
    password = models.CharField(max_length = 20, null = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nickname
