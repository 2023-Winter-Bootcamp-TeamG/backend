# Generated by Django 5.0.1 on 2024-01-16 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Frame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grid', models.CharField(max_length=10)),
                ('image', models.ImageField(upload_to='frames/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
