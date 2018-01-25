from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
from .serializers import ImageSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework import status, views
from django.http import HttpResponse
from images.models import Image
from django.core.files.images import ImageFile


# from images.npjson import JSONVectConverter
# from images.extract_cnn_vgg16_keras import extract_feat


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


"""
@csrf_exempt
def image_list(request):
    if request.method == 'GET':
        images = Image.objects.all()
        images_serializer = ImageSerializer(images, many=True)
        return JSONResponse(images_serializer.data)
    elif request.method == 'POST':
        print(request.content_type)
        image_data = MultiPartParser().parse(request)
        image_serializer = ImageSerializer(data=image_data['data'])
        if image_serializer.is_valid():
            image_serializer.save()
            return JSONResponse(image_serializer.data, status=status.HTTP_201_CREATED)
        return JSONResponse(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""


class ImageUploadView(views.APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        title_ = request.data['title']
        quote_ = request.data['quote']
        img = request.data['image']
        new_image = Image.objects.create(title=title_, quote=quote_, image=ImageFile(img))
        return JSONResponse(ImageSerializer(new_image).data, status=status.HTTP_201_CREATED)
