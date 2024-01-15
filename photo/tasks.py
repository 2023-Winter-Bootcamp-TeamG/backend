import boto3
from celery import shared_task
from django.core.files.base import ContentFile
import uuid
from .models import Photo
from member.models import Member
from myproject import settings

@shared_task
def save_photo_model(image_data, image_title, extension, member_id):
    # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
    image_name = f"{uuid.uuid4()}{extension}"

    member = Member.objects.get(id=member_id)

    result_image_file = ContentFile(image_data, name=image_name)

    photo = Photo(member_id=member, url=result_image_file, title=image_title)
    photo.save()

@shared_task
def delete_from_s3(image_url):
    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    s3.delete_object(Bucket=bucket_name, Key=image_url)

@shared_task
def update_photo(photo_id, image_data, original_file_name):
    photo = Photo.objects.get(id=photo_id)

    result_image_file = ContentFile(image_data, name=original_file_name)

    # 기존 Photo 객체의 url 필드 업데이트
    photo.url = result_image_file
    photo.save()
