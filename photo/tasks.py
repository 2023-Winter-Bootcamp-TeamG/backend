import boto3
from celery import shared_task
from django.core.files.base import ContentFile
import uuid
from .models import Photo, CustomedPhoto
from member.models import Member
from myproject import settings
from .serializers import CustomedPhotoSerializer

@shared_task
def save_photo_model(member_id, photo_data, photo_extension, result_photo_data, result_photo_extension, stickers_data, textboxes_data, result_photo_title):
    photo_name = f"{uuid.uuid4()}{photo_extension}"
    result_photo_name = f"{uuid.uuid4()}{result_photo_extension}"

    member = Member.objects.get(id=member_id)

    photo_file = ContentFile(photo_data, name=photo_name)
    photo = Photo(member_id=member, url=photo_file, is_customed=False)
    photo.save()

    result_photo_file = ContentFile(result_photo_data, name=result_photo_name)
    result_photo = Photo(member_id=member, url=result_photo_file, is_customed=True, title=result_photo_title)
    result_photo.save()

    customed_photo_data = {
        'photo_url': photo.url.url,
        'stickers': stickers_data,
        'textboxes': textboxes_data
    }

    serializer = CustomedPhotoSerializer(data=customed_photo_data)
    if serializer.is_valid():
        serializer.validated_data['user_id'] = member_id
        serializer.validated_data['photo_id'] = photo.id
        serializer.save()
    else:
        raise ValueError("Invalid customed photo data")

# def save_photo_model(image_data, image_title, extension, member_id):
#     # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
#     image_name = f"{uuid.uuid4()}{extension}"
#
#     member = Member.objects.get(id=member_id)
#
#     result_image_file = ContentFile(image_data, name=image_name)
#
#     photo = Photo(member_id=member, url=result_image_file, title=image_title)
#     photo.save()

@shared_task
def delete_from_s3(image_url):
    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    s3.delete_object(Bucket=bucket_name, Key=image_url)

@shared_task
def update_photo(photo_id, result_photo_data, original_file_name, stickers_data, textboxes_data):
    photo = Photo.objects.get(id=photo_id)

    result_image_file = ContentFile(result_photo_data, name=original_file_name)

    # 기존 Photo 객체의 url 필드 업데이트
    photo.url = result_image_file
    photo.save()

    customed_photo = CustomedPhoto.objects.using('mongodb').get(photo_id=photo_id)

    customed_photo.stickers = stickers_data
    customed_photo.textboxes= textboxes_data

    customed_photo.save(using='mongodb')