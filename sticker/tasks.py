import boto3
from celery import shared_task
from django.core.files.base import ContentFile
import uuid
from .models import Sticker
from member.models import Member
from myproject import settings
from rembg import remove
from io import BytesIO
import base64

@shared_task
def save_sticker_model(input_image, extension, member_id):
    # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
    image_name = f"{uuid.uuid4()}{extension}"

    output_image = remove(input_image)  # 변환된 바이트 데이터의 배경 제거

    # S3에 업로드 할 최종 이미지
    output_image_file = ContentFile(output_image, name=image_name)

    member = Member.objects.get(id=member_id)

    # Sticker 인스턴스 생성 및 저장
    sticker = Sticker(member_id=member, image=output_image_file)
    sticker.save()

@shared_task
def delete_from_s3(image_url):
    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3.delete_object(Bucket=bucket_name, Key=image_url)

@shared_task
def aisticker_url_encoding(dalleimage):
    buffered = BytesIO()  # 이미지를 메모리에 임시로 저장하기 위한 스트림 생성
    dalleimage.save(buffered, format="JPEG")  # dalleimage를 BytesIO 스트림에 저장
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')  # 인코딩
    return img_str