# Generated by Django 3.2.16 on 2023-12-17 20:10

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0008_auto_20231217_1928'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Comment',
            new_name='AddComment',
        ),
    ]