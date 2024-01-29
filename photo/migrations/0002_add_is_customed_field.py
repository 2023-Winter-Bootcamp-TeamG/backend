from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0001_initial'),  # 이전 마이그레이션 파일에 의존
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='is_customed',
            field=models.BooleanField(default=False),  # 새로운 필드 추가
        ),
    ]
