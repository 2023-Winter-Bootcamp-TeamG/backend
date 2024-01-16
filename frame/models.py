from django.db import models

# Create your models here.
class Frame(models.Model):
    grid = models.CharField(max_length=10, null=False)
    image = models.ImageField(upload_to='frames/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.grid