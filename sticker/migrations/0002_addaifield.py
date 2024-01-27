from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('sticker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sticker',
            name='is_ai',
            field=models.BooleanField(default=False),
        ),
    ]
