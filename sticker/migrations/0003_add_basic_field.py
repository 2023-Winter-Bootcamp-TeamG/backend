from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('sticker', '0002_addaifield'),
    ]

    operations = [
        migrations.AddField(
            model_name='sticker',
            name='is_basic',
            field=models.BooleanField(default=False),
        ),
    ]
