import sys, os, time, execnet, h5py

sys.path.append('/home/fede/Documenti/cnsearch/')
from django.core.management.base import BaseCommand
from images.models import Image
from images.npjson import JSONVectConverter
import numpy as np
from numpy import linalg as LA
from keras import Model
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input


def call_python_version(Version, Module, Function, ArgumentList):
    gw = execnet.makegateway("popen//python=python%s" % Version)
    channel = gw.remote_exec("""
        from %s import %s as the_function
        channel.send(the_function(*channel.receive()))
    """ % (Module, Function))
    channel.send(ArgumentList)
    return channel.receive()


def process_descs_matrix():
    print("entering in yael_script.py")
    result = call_python_version("2.7", "yael_script", "process",
                                 [])
    return result


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(u'.jpg')]


def extract_feat_from_CNN(tensor):
    # weights: 'imagenet'
    # pooling: 'max' or 'avg'
    # input_shape: (width, height, 3), width and height should >= 48

    input_shape = (224, 224, 3)
    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=False)
    t1 = time.time()
    feature_tensor = model.predict(tensor)
    t2 = time.time()
    print("Time to predict: " + str(t2 - t1))
    # feature_matrix = []
    # for feature_vector in feature_tensor:
    #    feature_matrix.append(feature_vector / LA.norm(feature_vector))
    # K.clear_session()
    # return feature_matrix
    print(feature_tensor.shape)
    # JSONVectConverter.save_vect_to_json("IMAGE_TENSOR", feature_tensor)
    # print("TENSOR SAVED ON DISK")
    return feature_tensor


def extract_feat_from_FCL(tensor):
    input_shape = (224, 224, 3)
    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=True)
    t1 = time.time()
    layer_name = "fc2"
    intermediate_layer_model = Model(inputs=model.input,
                                     outputs=model.get_layer(layer_name).output)
    feature_tensor = intermediate_layer_model.predict(tensor)
    t2 = time.time()
    print("Time to predict: " + str(t2 - t1))
    # feature_matrix = []
    # for feature_vector in feature_tensor:
    #    feature_matrix.append(feature_vector / LA.norm(feature_vector))
    # K.clear_session()
    # return feature_matrix
    print(feature_tensor.shape)
    return feature_tensor


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

        #Clean up the DB
        Image.objects.all().delete()
        img_list = get_imlist('img')

        #flag for avoiding recreate existing file -- set it manually
        exist_feature_matrix = True
        if not exist_feature_matrix:
            #Extract features
            feature_matrix = extract_feat_from_CNN(create_image_tensor(img_list))

            #Save datas, in order to communicate with Yael
            h5f = h5py.File("feature_matrix.h5", 'w')
            h5f.create_dataset('feature_matrix', data=feature_matrix)
            h5f.close()

            print("Feature extracted and saved on feature_matrix.h5")

        exist_image_fvs = False
        if not exist_image_fvs:
            #Call yael script
            result = process_descs_matrix()

            #Naive error handling
            if result == "YAEL SCRIPT: Mission accomplished!":
                print(result)
            else:
                print("ERROR")
                return

        #Open yael script computing results
        h5f = h5py.File("image_fvs.h5", 'r')
        image_fvs = h5f['image_fvs'][:]
        h5f.close()

        print("image_fvs opened. Size:")
        print(image_fvs.shape)

        for i, img_path in enumerate(img_list):
            new_image = Image.objects.create(
                title=os.path.splitext(os.path.split(img_path)[1])[0],
                image=img_path,
                signature=image_fvs[i].tolist()
            )
            #print("------------------------ " + new_image.title + " saved on DB -------------------")
