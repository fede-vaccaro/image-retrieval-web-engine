# Generated by Django 2.0.1 on 2018-01-19 23:05

from django.db import migrations, models
import images.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('image', models.ImageField(upload_to=images.models.upload_to)),
                ('created', models.DateField(auto_now_add=True)),
                ('quote', models.TextField()),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
    ]
