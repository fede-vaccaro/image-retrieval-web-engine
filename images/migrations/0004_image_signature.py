# Generated by Django 2.0.1 on 2018-01-21 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20180121_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='signature',
            field=models.TextField(null=True),
        ),
    ]
