# photo/migrations/0003_add_origin_field.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0002_add_is_customed_field'),  # 이전 마이그레이션 파일에 의존
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='origin',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='derived_photos', to='photo.photo'),
        ),
    ]
