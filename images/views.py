from django.shortcuts import render
from django.shortcuts import redirect
from .forms import ImageForm
from .models import Image
from .npjson import JSONVectConverter
from django.conf import settings
from .extract_cnn_vgg16_keras import extract_feat
from django.core.files.storage import FileSystemStorage
import numpy as np
from django.db.models import FloatField, Case, Value, When
import os, time



# Create your views here.


def add_image(request):
    if request.method == "POST":
        form = ImageForm(
            data=request.POST,
            files=request.FILES,
        )
        if form.is_valid():
            image = form.save()
            image.signature = JSONVectConverter.vect_to_json(extract_feat(settings.BASE_DIR + "/" + image.image.name))
            image.save()
            return redirect("images/add_image.html")
    elif request.method == "GET":
        form = ImageForm()
        return render(request, "images/add_image.html", {'form': form})

    return render(request, "images/add_image.html", {'form': form})


def image_list(request):
    image_list = Image.objects.all().order_by('?')
    return render(request, 'images/image_list.html', {'image_list': image_list})


def query(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        print("XXX" + settings.MEDIA_ROOT + "/temp")
        location = settings.MEDIA_ROOT + "/temp"
        fs = FileSystemStorage(location=location, base_url=settings.MEDIA_URL + "/cache")
        filename = fs.save(myfile.name, myfile)
        #uploaded_file_url = fs.url(filename)
        # return render(request, 'images/query.html', {
        #    'uploaded_file_url': uploaded_file_url
        # })
        filename_base = os.path.splitext(myfile.name)
        return redirect('/images/sorted/' + filename_base[0] + "/")
    return render(request, 'images/query.html')


"""
def image_sorted(request):
    query_signature = extract_feat(settings.MEDIA_ROOT + "/cache" + "/003_ant_image_0003.jpg")

    image_list = Image.objects.annotate(score=np.dot(
        JSONVectConverter.json_to_vect(F('signature')), query_signature.T
    ).astype(float)).order_by('score')
    return render(request, 'images/sorted.html', {'image_sorted': image_list})
"""


def image_sorted(request, image_path):
    query_signature = extract_feat(settings.MEDIA_ROOT + "/temp/" + image_path + ".jpg")  # a NumPy-Array object
    start = time.time()
    print("start counting")

    value_dict = {}
    for image in Image.objects.all():
        S = image.signature
        value_dict[image.id] = np.dot(
            JSONVectConverter.json_to_vect(S),
            query_signature.T
        ).astype(float)

    flat = sorted(value_dict, key=value_dict.__getitem__)[::-1] # lista ordinata delle PK degli elementi da visualizzare
    #print(sorted(value_dict, key=value_dict.__getitem__))
    #print(sorted(value_dict.values()))
    end = time.time()
    print(end - start) # quanto impiega a svolgere il mega prodotto scalare
    '''
    whens = [
        When(signature=k, then=v) for k, v in value_dict.items()
    ]

    qs = Image.objects.all().annotate(
        score=Case(
            *whens,
            default=0,
            output_field=FloatField()
        )
    ).order_by('-score')
    '''
    qs_new = []
    nToDisplay = 30
    flat = flat[:nToDisplay]
    for i in range(len(flat)):
        qs_new.append(Image.objects.get(id=flat[i]))
    end = time.time()
    print(end - start)
    return render(request, 'images/sorted.html', {'image_sorted': qs_new})

