import os, time, math, gc
from keras import Model
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from skimage import data, transform
from sklearn.feature_extraction import image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


def get_imlist(path):
    print("Getting image list")
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(u'.jpg')]


def create_image_tensor(img_list, batch_size = 6):
    total_batch = math.ceil(len(img_list) / batch_size)
    batch_num = 0

    tensor = []
    for i, path in enumerate(img_list, 1):
        absolute_path = os.path.dirname(__file__)
        img = data.load(os.path.join(absolute_path, path))
        print("appending image %s" %i)
        tensor.append(img)
        if i % batch_size == 0:
            batch_num+=1
            print("Yielding image tensor, batch number: %s/%s" %(batch_num, total_batch))
            tensor = np.array(tensor)
            print("Tensor shape is : %s" %(tensor.shape))
            yield np.array(tensor)
            tensor = []
            gc.collect()
        if i == len(img_list):
            batch_num+=1
            print("Yielding last image tensor: %s/%s" %(batch_num, total_batch))
            yield np.array(tensor)
            tensor = []
            gc.collect()

    #tensor = np.array(tensor)
    #return tensor


def create_bag_of_window(tensorGenerator, n_patches = 800):
    config = tf.ConfigProto(
        device_count={'GPU': 0}
    )
    for tensor in tensorGenerator:
        sess = tf.Session(config=config)
        for img in tensor:
            t0 = time.time()
            print("Creating bag of Window")# a tensor of shape %s" %tensor.shape)
            patches = image.extract_patches_2d(img, patch_size=(int(img.shape[0] / 10), int(img.shape[1] / 10)), max_patches=n_patches)
            # with tf.Session():
            #     patches = tf.image.resize_images(patches, size=(224, 224))
            #     img_ = transform.resize(img, (224, 224, 3))
            #     img_ = np.expand_dims(img_, axis=0)
            #     patches = tf.concat([patches, img_], 0)
            #     print("patches.shape is: %s" % patches.shape)
            #     patches = patches.eval()
            #     patches = preprocess_input(patches)
            #     print("yelding patches")
            # yield patches
            patches_ = []
            for patch in patches:
                p = transform.resize(patch, (224, 224, 3))
                patches_.append(p)
            img_ = transform.resize(img, (224, 224, 3))
            patches_.append(img_)
            t1 = time.time()
            print("Time to create the bag of window: %ss" %(t1-t0))
            yield np.array(patches_)
    #return np.array(completeTensor)

def extract_feat_from_FCL(generator_):
    input_shape = (224, 224, 3)
    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=True)
    t1 = time.time()
    layer_name = "fc2"
    intermediate_layer_model = Model(inputs=model.input,
                                     outputs=model.get_layer(layer_name).output)

    for item in generator:
        t0 = time.time()
        feature_tensor = intermediate_layer_model.predict(item)
        t1 = time.time()
        print("time to predict : %ss" %(t1-t0))
        gc.collect()
        print(feature_tensor.shape)

    #feature_tensor = intermediate_layer_model.predict_generator(generator=generator_, steps=1, max_queue_size=1)
    t2 = time.time()
    print("Total time to predict: " + str(t2 - t1))
    print(feature_tensor.shape)
    return feature_tensor

def modify(x):
    sess = tf.Session()

    with sess.as_default():
        print('Type', type(x))  # debug
        xarr = x.eval()  # convert to a numpy
        print('Type', type(xarr))
        return xarr

img_list = get_imlist("img/")
tensor = create_image_tensor(img_list)
# batch_size = 2
# total_images = tensor.shape[0]
# print(total_images)
# total_pages = int(total_images/batch_size)
# print(total_pages)
#
# for p in range(total_pages + 1):
#     start = p*batch_size
#     end = (p+1)*batch_size
#     if end > total_images:
#         end = total_images

generator = create_bag_of_window(tensor)

#for g in generator:
#    print(g.shape)

extract_feat_from_FCL(generator)

# completeTensor = create_bag_of_window(tensor)
# print(completeTensor[0].shape)
# element = completeTensor[0]
#
# sess = tf.InteractiveSession()
# element = preprocess_input(element)
# print(type(element))
#
# extract_feat_from_FCL(element.eval())

