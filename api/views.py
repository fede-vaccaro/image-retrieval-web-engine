from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from .serializers import ImageSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework import status, views, response, generics, pagination
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from django.http import HttpResponse
from images.models import Image
from images.extract_cnn_vgg16_keras import extract_feat_CNN, extract_feat_FCL, extract_feat_FCL_from_img
from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from taggit.models import Tag
import PIL
import os, time, math
import numpy as np
import numexpr as ne
import uuid


def query_over_db(query_signature, page):

    query_signature = np.array(query_signature)

    t0 = time.time()

    descriptor_matrix = cache.get('descriptor_matrix')
    id_vector = cache.get('id_vector')

    if not descriptor_matrix:
        id_vector = []
        descriptor_matrix = []
        images_dict = Image.objects.all().values('id', 'signature')
        for image in images_dict:
            s = image['signature']
            descriptor = np.array(s)
            descriptor_matrix.append(descriptor)
            id_vector.append(image['id'])

        cache.set('id_vector', id_vector)
        cache.set('descriptor_matrix', descriptor_matrix)

    t1 = time.time()
    print("time to pull out the descriptors : " + str(t1 - t0))
    t1 = time.time()
    #result = np.abs(np.dot(descriptor_matrix, query_signature.T))

    #result = np.sum((descriptor_matrix - query_signature)**2, axis=1)

    result = ne.evaluate('sum((descriptor_matrix - query_signature)**2, axis=1)')

    t2 = time.time()
    print("time to calculate similarity: " + str(t2 - t1))

    perm = np.argsort(result)[(page - 1) * 30:page * 30]
    print(perm.shape)
    print(len(id_vector))

    perm_id = np.array(id_vector)[perm]
    print(len(perm_id))

    print("printing sort")
    print(np.sort(result)[0])

    t4 = time.time()

    print("time to order the result: " + str(t4 - t2))

    qs = Image.objects.defer('signature').filter(id__in=perm_id.tolist())

    qs_new = []
    for i in range(len(perm_id)):
        qs_new.append(qs.get(id=perm_id[i]))

    t3 = time.time()
    print("time to get the results from the DB : " + str(t3 - t2))
    print("total time : " + str(t3 - t0))
    print(result[perm])
    return qs_new


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


class RetrieveByTagView(generics.ListAPIView):
    def get(self, request, tag):
        tags = get_object_or_404(Tag, slug=tag)
        images = Image.objects.filter(tags__in=[tags])
        paginator = YourPagination()
        page = paginator.paginate_queryset(images, request)
        images_serializer = ImageSerializer(page, many=True)
        return paginator.get_paginated_response(images_serializer.data)

class ImageListView(generics.ListAPIView):
    def get(self, request):
        images = Image.objects.all().order_by('?')
        paginator = YourPagination()
        page = paginator.paginate_queryset(images, request)
        images_serializer = ImageSerializer(page, many=True)
        return paginator.get_paginated_response(images_serializer.data)


class ExploreView(generics.ListAPIView):
    def get(self, request, pk):
        print()
        print("start counting")
        t1 = time.time()

        sign = Image.objects.values('signature').get(pk=pk)
        query_signature = np.array(sign['signature'])
        qs_new = query_over_db(query_signature, int(request.GET['page']))

        t2 = time.time()

        print("total time to explore: " + str(t2 - t1))

        images_serializer = ImageSerializer(qs_new, many=True)

        return response.Response({
            'results': images_serializer.data,
            'total_pages': math.ceil(Image.objects.count() / api_settings.PAGE_SIZE),
        })


@csrf_exempt
def get_image(request, pk):
    if request.method == 'GET':
        image = get_object_or_404(Image.objects.all(), pk=pk)
        return JSONResponse(ImageSerializer(image).data, status=status.HTTP_202_ACCEPTED)

@csrf_exempt
def retrieve_tags(request):
    if request.method == 'GET':
        tags = Image.tags.values('slug')
        tags_vect = []
        for tag in tags:
            tags_vect.append(tag['slug'])
        return JSONResponse(tags_vect)

class OverAllowedDimension(Exception):

    def __init__(self, maxAllowedDim, thisDim):
        self.maxAllowedDim = maxAllowedDim
        self.thisDim = thisDim
        self.message = "Sent file is bigger than allowed: " + str(thisDim) + " > " + str(maxAllowedDim) + " !"
        print(self.message)




@csrf_exempt
def query_up(request):
    if request.method == 'POST':
        try:
            myfile = request.FILES['myfile']
            print(myfile._size)
            allowed_dimension = 3145728
            if (myfile._size > allowed_dimension):
                raise OverAllowedDimension(allowed_dimension, myfile._size)
        except OverAllowedDimension as err:
            print(err.message)
            return HttpResponse(err.message, status=status.HTTP_400_BAD_REQUEST)
        except:
            return HttpResponse("something went wrong.", status=status.HTTP_400_BAD_REQUEST)

        img = PIL.Image.open(myfile)
        img = img.resize((224, 224), PIL.Image.ANTIALIAS)
        t = time.time()
        query_signature = extract_feat_FCL(img, predict_tags=False)
        print("time to extract features of {0} : {1}s".format(myfile.name, time.time() - t))
        identifier = uuid.uuid4()
        cache.set(identifier, query_signature, 60*5)

        print("ID generated is {}".format(identifier))


        return HttpResponse(identifier, status=status.HTTP_202_ACCEPTED)


class QueryGetView(generics.ListAPIView):
    def get(self, request, identifier):
        print("start counting")
        t1 = time.time()

        query_signature = cache.get(identifier).tolist()

        if not query_signature[0]:
            "identifier {} doesn't exists.".format(identifier)
            return HttpResponse("Asking for an inexistent identifier: error. Maybe is your session expired?", status=status.HTTP_400_BAD_REQUEST)

        qs_new = query_over_db(query_signature, int(request.GET['page']))

        t2 = time.time()
        print("time with tensorflow loading : " + str(t2 - t1))


        images_serializer = ImageSerializer(qs_new, many=True)

        return response.Response({
            'results': images_serializer.data,
            'total_pages': math.ceil(Image.objects.count() / api_settings.PAGE_SIZE),
        })


class ImageUploadView(views.APIView):
    parser_classes = (MultiPartParser,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        title_ = request.data['title']
        quote_ = request.data['quote']

        try:
            img = request.data['image']
            print(img)
            allowed_dimension = 3145728
            if (img._size > allowed_dimension):
                raise OverAllowedDimension(allowed_dimension, img._size)
        except OverAllowedDimension as err:
            print(err.message)
            return HttpResponse(err.message, status=status.HTTP_400_BAD_REQUEST)
        except:
            return HttpResponse("something went wrong.", status=status.HTTP_400_BAD_REQUEST)
        try:
            new_image = Image.objects.create(title=title_, quote=quote_, image=ImageFile(img))

            image = PIL.Image.open(img)
            image = image.resize((224, 224), PIL.Image.ANTIALIAS)


            signature_, tags = extract_feat_FCL(image, predict_tags=True)
            new_image.signature = signature_[0].tolist()
            for tag in tags:
                new_image.tags.add(tag)
            new_image.save()
        except:
            new_image.delete()
            return HttpResponse("something went wrong while inserting the image.", status=status.HTTP_400_BAD_REQUEST)

        id_vector = cache.get('id_vector')
        descriptor_matrix = cache.get('descriptor_matrix')

        if descriptor_matrix:
            s = new_image.signature
            descriptor = np.array(s)
            descriptor_matrix.append(descriptor)
            id_vector.append(new_image.id)
            cache.set('id_vector', id_vector)
            cache.set('descriptor_matrix', descriptor_matrix)

        return JSONResponse(ImageSerializer(new_image).data, status=status.HTTP_201_CREATED)
