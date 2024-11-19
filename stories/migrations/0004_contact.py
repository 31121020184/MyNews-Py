# Generated by Django 5.0.7 on 2024-09-09 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0003_story_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20, null=True)),
                ('subject', models.CharField(max_length=264)),
                ('message', models.TextField()),
            ],
        ),
    ]
