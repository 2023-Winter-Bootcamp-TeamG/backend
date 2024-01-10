from django import forms
from .models import Photo

#모델 폼 정의
class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'url']