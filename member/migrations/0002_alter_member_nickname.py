# Generated by Django 5.0.1 on 2024-01-08 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='nickname',
            field=models.CharField(max_length=20),
        ),
    ]
