from rest_framework import serializers
from images.models import Image
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField


class ImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    thumbnail = HyperlinkedSorlImageField(
        '220x220',
        options={"crop": "center"},
        source='image',
        read_only=True
    )

    class Meta:
        model = Image
        fields = ['pk', 'title', 'image', 'quote', 'tags','thumbnail']
