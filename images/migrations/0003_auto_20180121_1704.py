# Generated by Django 2.0.1 on 2018-01-21 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_remove_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='img/'),
        ),
    ]
