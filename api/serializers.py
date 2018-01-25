from rest_framework import serializers
from images.models import Image

class ImageSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    image = serializers.ImageField(use_url=True)
    quote = serializers.CharField(allow_blank=True)

    def create(self, validated_data):
        return Image.objects.create(**validated_data)
