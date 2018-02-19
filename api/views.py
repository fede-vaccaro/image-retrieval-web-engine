from django.views.decorators.csrf import csrf_exempt
from .serializers import ImageSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework import status, views, response, generics, pagination
from rest_framework.settings import api_settings
from django.conf import settings
from django.http import HttpResponse
from images.models import Image
from images.extract_cnn_vgg16_keras import extract_feat_CNN, extract_feat_FCL
from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
import os, time, math
import numpy as np
import heapq


def query_over_db(query_signature, page):
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
    #result = np.abs(np.dot(descriptor_matrix, query_signature.T))
    result = np.sum((descriptor_matrix - query_signature)**2, axis=1)

    t2 = time.time()
    print("time to make the big dot product: " + str(t2 - t1))

    perm = np.argsort(result)[(page - 1) * 30:page * 30]
    perm_id = np.array(id_vector)[perm]

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


def query_over_db_(query_signature, page):
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

    result = np.dot(descriptor_matrix, query_signature)

    t2 = time.time()
    print("time to make the big dot product: " + str(t2 - t1))

    value_dict = []

    for i in range(len(id_vector)):
        heapq.heappush(value_dict, (1 - result[i], id_vector[i]))

    page_size = api_settings.PAGE_SIZE
    value_dict = value_dict[(page - 1) * page_size:page * page_size]

    t4 = time.time()

    print("time to order the result: " + str(t4 - t2))

    db = Image.objects.defer('signature').filter(id__in=[j for i, j in value_dict])

    qs_new = [None] * page_size
    i = 0
    for value, id in value_dict:
        qs_new[i] = db.get(id=id)
        i += 1

    t3 = time.time()
    print("time to get the results from the DB : " + str(t3 - t2))
    print("total time : " + str(t3 - t0))
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
        location = settings.MEDIA_ROOT + "/temp"
        fs = FileSystemStorage(location=location, base_url=settings.MEDIA_URL + "/cache")
        fs.save(myfile.name, myfile)
        filename_base = os.path.splitext(myfile.name)
        image_path = filename_base[0]
        return HttpResponse(image_path, status=status.HTTP_202_ACCEPTED)


class QueryGetView(generics.ListAPIView):
    def get(self, request, img_name):
        print("start counting")
        t1 = time.time()

        query_signature = extract_feat_CNN(
            settings.MEDIA_ROOT + "/temp/" + img_name + ".jpg")  # a NumPy-Array object
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
        new_image = Image.objects.create(title=title_, quote=quote_, image=ImageFile(img))
        new_image.signature = (extract_feat_CNN(settings.BASE_DIR + "/" + new_image.image.name)).tolist()
        new_image.save()

        id_vector = cache.get('id_vector')
        descriptor_matrix = cache.get('descriptor_matrix')

        if not descriptor_matrix:
            id_vector = []
            descriptor_matrix = []
            for image in Image.objects.all():
                s = image.signature
                descriptor = np.array(s)
                descriptor_matrix.append(descriptor)
                id_vector.append(image.id)

            cache.set('id_vector', id_vector)
            cache.set('descriptor_matrix', descriptor_matrix)
        else:
            s = new_image.signature
            descriptor = np.array(s)
            descriptor_matrix.append(descriptor)
            id_vector.append(new_image.id)
            cache.set('id_vector', id_vector)
            cache.set('descriptor_matrix', descriptor_matrix)

        return JSONResponse(ImageSerializer(new_image).data, status=status.HTTP_201_CREATED)
