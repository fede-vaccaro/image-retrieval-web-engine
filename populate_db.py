import sys, os
sys.path.append('C:/Users/Federico/image_prova/Scripts/image_prova')
from django.core.management.base import BaseCommand
from django.conf import settings
from images.models import Image
from images.npjson import JSONVectConverter
from images.extract_cnn_vgg16_keras import extract_feat

def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(u'.jpg')]


class Command(BaseCommand):
    def handle(self, *args, **options):
        Image.objects.all().delete()
        img_list = get_imlist('img')
        for i, img_path in enumerate(img_list):
            new_image = Image.objects.create()
            new_image.title = os.path.splitext(os.path.split(img_path)[1])[0]
            new_image.image = img_path
            new_image.signature = JSONVectConverter.vect_to_json(extract_feat(settings.BASE_DIR + "/" + new_image.image.name))
            new_image.save()










