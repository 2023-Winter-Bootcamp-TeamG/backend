from celery import shared_task
from django.core.files.base import ContentFile
import uuid
from .models import Photo
from member.models import Member

@shared_task
def save_photo_model(image_data, image_title, extension, member_id):
    # 고유한 파일명 생성(S3는 같은 이름의 파일을 업로드할 시 덮어쓰기 때문)
    image_name = f"{uuid.uuid4()}{extension}"

    member = Member.objects.get(id=member_id)

    result_image_file = ContentFile(image_data, name=image_name)

    photo = Photo(member_id=member, url=result_image_file, title=image_title)
    photo.save()

