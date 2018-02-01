from django.views.decorators.csrf import csrf_exempt
from .serializers import ImageSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework import status, views, response, generics, pagination
from rest_framework.settings import api_settings
from django.conf import settings
from django.http import HttpResponse
from images.models import Image
from images.npjson import JSONVectConverter
from images.extract_cnn_vgg16_keras import extract_feat
from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
import os, time
import numpy as np


# from images.npjson import JSONVectConverter
# from images.extract_cnn_vgg16_keras import extract_feat


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class YourPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):
        return response.Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


@csrf_exempt
def image_list(request):
    if request.method == 'GET':
        images = Image.objects.all().order_by('?')
        images_serializer = ImageSerializer(images, many=True)
        return JSONResponse(images_serializer.data, status=status.HTTP_202_ACCEPTED)


class ImageListView(generics.ListAPIView):
    def get(self, request):
        images = Image.objects.all().order_by('?')
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = YourPagination()
        page = paginator.paginate_queryset(images, request)
        images_serializer = ImageSerializer(page, many=True)
        return paginator.get_paginated_response(images_serializer.data)


class ExploreView(generics.ListAPIView):
    def get(self, request, pk):

        sign = Image.objects.get(pk=pk).signature
        query = JSONVectConverter.json_to_vect(sign)

        value_dict = {}
        for image in Image.objects.all():
            S = image.signature
            value_dict[image.id] = np.dot(
                JSONVectConverter.json_to_vect(S),
                query.T
            ).astype(float)

        flat = sorted(value_dict, key=value_dict.__getitem__)[
               ::-1]  # lista ordinata delle PK degli elementi da visualizzare
        qs_new = []
        # nToDisplay = 30
        # flat = flat[:nToDisplay]
        for i in range(len(flat)):
            qs_new.append(Image.objects.get(id=flat[i]))

        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = YourPagination()
        page = paginator.paginate_queryset(qs_new, request)
        images_serializer = ImageSerializer(page, many=True)
        return paginator.get_paginated_response(images_serializer.data)


@csrf_exempt
def get_image(request, pk):
    if request.method == 'GET':
        image = get_object_or_404(Image.objects.all(), pk=pk)
        return JSONResponse(ImageSerializer(image).data, status=status.HTTP_202_ACCEPTED)


@csrf_exempt
def query_up(request):
    if request.method == 'POST':
        myfile = request.FILES['myfile']
        #print("XXX" + settings.MEDIA_ROOT + "/temp")
        location = settings.MEDIA_ROOT + "/temp"
        fs = FileSystemStorage(location=location, base_url=settings.MEDIA_URL + "/cache")
        fs.save(myfile.name, myfile)
        filename_base = os.path.splitext(myfile.name)
        image_path = filename_base[0]
        return HttpResponse(image_path, status=status.HTTP_202_ACCEPTED)


class QueryGetView(generics.ListAPIView):
    def get(self, request, img_name):
        start = time.time()
        print("start counting")
        query_signature = extract_feat(settings.MEDIA_ROOT + "/temp/" + img_name + ".jpg")  # a NumPy-Array object
        # print(query_signature)

        value_dict = {}
        for image in Image.objects.all():
            S = image.signature
            value_dict[image.id] = np.dot(
                JSONVectConverter.json_to_vect(S),
                query_signature.T
            ).astype(float)

        flat = sorted(value_dict, key=value_dict.__getitem__)[
               ::-1]  # lista ordinata delle PK degli elementi da visualizzare
        # print(sorted(value_dict, key=value_dict.__getitem__))
        # print(sorted(value_dict.values()))
        end = time.time()
        print(end - start)  # quanto impiega a svolgere il mega prodotto scalare

        qs_new = []
        # nToDisplay = 30
        # flat = flat[:nToDisplay]
        for i in range(len(flat)):
            qs_new.append(Image.objects.get(id=flat[i]))
        end = time.time()
        # images_serializer = ImageSerializer(qs_new, many=True)
        print(end - start)

        paginator = YourPagination()
        page = paginator.paginate_queryset(qs_new, request)
        images_serializer = ImageSerializer(page, many=True)
        return paginator.get_paginated_response(images_serializer.data)


class ImageUploadView(views.APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        title_ = request.data['title']
        quote_ = request.data['quote']
        img = request.data['image']
        if (img == "undefined"):
            return HttpResponse("something went wrong.", status=status.HTTP_400_BAD_REQUEST)
        new_image = Image.objects.create(title=title_, quote=quote_, image=ImageFile(img))
        return JSONResponse(ImageSerializer(new_image).data, status=status.HTTP_201_CREATED)
