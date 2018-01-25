import sys, os

sys.path.append('C:/Users/Federico/image_prova/Scripts/image_prova')
from django.core.management.base import BaseCommand
from images.models import Image
from images.npjson import JSONVectConverter
import numpy as np
from numpy import linalg as LA
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(u'.jpg')]


def extract_feat(tensor):
    # weights: 'imagenet'
    # pooling: 'max' or 'avg'
    # input_shape: (width, height, 3), width and height should >= 48

    input_shape = (224, 224, 3)
    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=False)

    feature_tensor = model.predict(tensor)
    feature_matrix = []
    for feature_vector in feature_tensor:
        feature_matrix.append(feature_vector / LA.norm(feature_vector))
    # K.clear_session()
    return feature_matrix


def create_image_tensor(img_list):
    input_shape = (224, 224, 3)
    tensor = []
    for path in img_list:
        img = image.load_img(path, target_size=(input_shape[0], input_shape[1]))
        img = image.img_to_array(img)
        img = preprocess_input(img)
        tensor.append(img)
    tensor = np.array(tensor)
    return tensor


class Command(BaseCommand):
    def handle(self, *args, **options):
        Image.objects.all().delete()
        img_list = get_imlist('img')

        feature_matrix = extract_feat(create_image_tensor(img_list))

        for i, img_path in enumerate(img_list):
            new_image = Image.objects.create(
                title=os.path.splitext(os.path.split(img_path)[1])[0],
                image=img_path,
                signature=JSONVectConverter.vect_to_json(feature_matrix[i])
            )
            print("------------------------ " + new_image.title + " saved on DB -------------------")
