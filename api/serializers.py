from rest_framework import serializers
from images.models import Image
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

class ImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = Image
        fields = ['pk', 'title', 'image', 'quote', 'tags']
