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

    # 원본 사진 저장
    photo_file = ContentFile(photo_data, name=photo_name)
    photo = Photo(member_id=member, url=photo_file, is_customed=False)
    photo.save()

    # 결과 사진 저장
    result_photo_file = ContentFile(result_photo_data, name=result_photo_name)
    result_photo = Photo(member_id=member, url=result_photo_file, is_customed=True, title=result_photo_title, origin=photo)
    result_photo.save()

    customed_photo_data = {
        'photo_url': photo.url.url,
        'stickers': stickers_data,
        'textboxes': textboxes_data
    }

    # 원본 사진, 스티커, 텍스트박스 몽고디비에 저장
    serializer = CustomedPhotoSerializer(data=customed_photo_data)
    if serializer.is_valid():
        serializer.validated_data['user_id'] = member_id
        serializer.validated_data['photo_id'] = photo.id
        serializer.save()
    else:
        raise ValueError("Invalid customed photo data")

@shared_task
def delete_from_s3(photo_id, image_url, result_image_url):
    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    CustomedPhoto.objects.using('mongodb').filter(photo_id=photo_id).delete() # 해당 커스텀 목록 삭제
    s3.delete_object(Bucket=bucket_name, Key=image_url) # 원본사진 삭제
    s3.delete_object(Bucket=bucket_name, Key=result_image_url) # 결과사진 삭제


@shared_task
def update_photo(photo_id, result_photo_data, original_file_name, stickers_data, textboxes_data):
    photo = Photo.objects.get(id=photo_id)

    # 기존 이미지 파일의 이름을 가진 새로운 이미지 파일 저장 -> S3는 같은 이름의 파일을 덮어씀
    result_image_file = ContentFile(result_photo_data, name=original_file_name)

    # 기존 Photo 객체의 url 필드 업데이트
    photo.url = result_image_file
    photo.save()

    customed_photo = CustomedPhoto.objects.using('mongodb').get(photo_id=photo_id)

    updated_photo_data = {
        'photo_url': customed_photo.photo_url,
        'stickers': stickers_data,
        'textboxes': textboxes_data
    }

    serializer = CustomedPhotoSerializer(customed_photo, data=updated_photo_data, partial=True)
    if serializer.is_valid():
        # 기존 몽고디비 객체 삭제하고 새로운 객체 저장, 원래 코드상으로는 수정이 되야하는 건데 자꾸 새로운 객체로 저장돼서 기존꺼 삭제하는 걸로...
        CustomedPhoto.objects.using('mongodb').filter(photo_id=photo_id).delete()
        serializer.save(using='mongodb')
    else:
        raise ValueError("Invalid customed photo data")
