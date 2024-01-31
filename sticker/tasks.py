import base64
import boto3
from celery import shared_task
from django.core.files.base import ContentFile
import uuid
from .models import Sticker
from member.models import Member
from myproject import settings
from rembg import remove
from io import BytesIO
import requests
from PIL import Image
from openai import OpenAI
import re

@shared_task
def save_sticker_model(input_image, extension, member_id, is_ai):
    # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
    image_name = f"{uuid.uuid4()}{extension}"

    output_image = remove(input_image)  # 변환된 바이트 데이터의 배경 제거

    # S3에 업로드 할 최종 이미지
    output_image_file = ContentFile(output_image, name=image_name)

    member = Member.objects.get(id=member_id)

    # Sticker 인스턴스 생성 및 저장
    sticker = Sticker(member_id=member, image=output_image_file, is_ai=is_ai)
    sticker.save()

@shared_task
def delete_from_s3(image_url):
    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3.delete_object(Bucket=bucket_name, Key=image_url)

@shared_task
def aisticker_create(keyword):

    client = OpenAI(api_key=settings.AI_STICKER_KEY)

    # 이미지 생성
    url_response = client.images.generate(
        model="dall-e-3",
        prompt=keyword + " 스티커",  # 만들 스티커 단어 입력
        n=1,
        size="1024x1024"
    )

    # # 생성된 이미지의 URL 추출
    aisticker_url = url_response['data'][0]['url']  # 이미지 url 출력
    # image_response = requests.get(aisticker_url)
    # dalleimage = Image.open(BytesIO(image_response.content))
    #
    # # 이미지를 메모리에 임시로 저장하기 위한 스트림 생성
    # buffered = BytesIO()
    #
    # # dalleimage를 BytesIO 스트림에 저장
    # dalleimage.save(buffered, format="JPEG")
    #
    # img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return aisticker_url

@shared_task
def save_aisticker_model(img_str, member_id, is_ai):
    ######################
    image_response = requests.get(img_str)
    dalleimage = Image.open(BytesIO(image_response.content))

    # 이미지를 메모리에 임시로 저장하기 위한 스트림 생성
    buffered = BytesIO()

    # dalleimage를 BytesIO 스트림에 저장
    dalleimage.save(buffered, format="PNG")

    img_result = base64.b64encode(buffered.getvalue()).decode('utf-8')
    #################################
    # 이미지 데이터 디코딩
    input_image = base64.b64decode(img_result)

    # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
    image_name = f"{uuid.uuid4()}.png"

    # 변환된 바이트 데이터의 배경 제거
    output_image = remove(input_image)

    # S3에 업로드 할 최종 이미지
    output_image_file = ContentFile(output_image, name=image_name)

    member = Member.objects.get(id=member_id)

    # Sticker 인스턴스 생성 및 저장
    sticker = Sticker(member_id=member, image=output_image_file, is_ai=is_ai)
    sticker.save()