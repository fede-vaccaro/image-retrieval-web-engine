import os, time, math, gc
from keras import Model
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from skimage import data, transform
from sklearn.feature_extraction import image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from mpipe import OrderedStage, Pipeline
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool
from scipy.misc import imsave
import pathlib



def resize(img):
    return transform.resize(img, (224, 224, 3))


# function to be mapped over
def calculateParallel(tensor, threads=16):
    pool = ThreadPool(threads)
    results = pool.map(resize, tensor)
    pool.close()
    pool.join()
    return np.array(results)


def get_imlist(path):
    print("Getting image list")
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(u'.jpg')]


def send_batch(list):
    print("Opening image")
    tensor = [None] * len(list)
    for i, path in enumerate(list):
        absolute_path = os.path.dirname(__file__)
        img = data.load(os.path.join(absolute_path, path))
        print("appending image %s" % i)
        tensor[i] = img
    # gc.collect()
    return tensor


def create_bag_of_window(tensor):
    # gc.collect()
    n_patches = 500
    batch = [None] * len(tensor)
    for i, img in enumerate(tensor):
        t0 = time.time()
        print("Creating bag of Window")  # a tensor of shape %s" %tensor.shape)
        patches = image.extract_patches_2d(img, patch_size=(int(img.shape[0] / 10), int(img.shape[1] / 10)),
                                           max_patches=n_patches)

        # t2 = time.time()
        # patches_ = calculateParallel(patches, 16)
        # t3 = time.time()
        # print("Time to resize all the patches in parallel {}s".format(t3 - t2))
        # del patches
        img = np.expand_dims(transform.resize(img, (224, 224, 3)), axis=0)
        #batch[i] = np.vstack((img, patches))
        batch_ = []
        batch_.append(img)
        batch_.append(patches)
        batch[i] = batch_
        del img
        del patches
        t1 = time.time()
        print("Time to create the bag of window: %ss" % (t1 - t0))

    gc.collect()
    return batch
    # return np.array(completeTensor)


def extract_feat_from_FCL():
    input_shape = (224, 224, 3)
    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=True)
    t1 = time.time()
    layer_name = "fc2"
    intermediate_layer_model = Model(inputs=model.input,
                                     outputs=model.get_layer(layer_name).output)

    list = get_imlist("img_cut")

    stage1 = OrderedStage(send_batch)
    stage2 = OrderedStage(create_bag_of_window)
    stage1.link(stage2)
    pipe = Pipeline(stage1)

    batch_size = 1
    total_batch = math.ceil(len(list) / batch_size)

    for p in range(total_batch):
        v = list[p * batch_size:(p + 1) * batch_size]
        print("Batch number %s" % p)
        pipe.put(v)

    pipe.put(None)

    for result in pipe.results():
        t0 = time.time()
        print("Predicting...")
        feature_tensor = intermediate_layer_model.predict(
            np.vstack((r for r in result))
        )
        t1 = time.time()
        print("time to predict : %ss" % (t1 - t0))
        # gc.collect()
        print(feature_tensor.shape)
        del result

    # feature_tensor = intermediate_layer_model.predict_generator(generator=generator_, steps=1, max_queue_size=1)
    t2 = time.time()
    print("Total time to predict: " + str(t2 - t1))
    print(feature_tensor.shape)
    return feature_tensor


# gc.enable()
# t = time.time()
# extract_feat_from_FCL()
# print("TOTAL TIME WITH MPIPE = {}".format(time.time() - t))

global n_patches
n_patches = 500
global image_index
image_index = 0
global window_index
window_index = 0

def last_stage(result):
    global window_index
    global image_index
    global n_patches
    for im_w in result: #np.vstack((r for r in result)):
        for im in im_w:
            for i in im:
                #print("IM_W[0] shape IS {0} IM_W[1] shape is {1}".format(im_w[0].shape, im_w[1].shape))
                #print("I SHAPE IS {}".format(i.shape))

                pathlib.Path('img_windowed/image_{0}_'.format(image_index)).mkdir(parents=True, exist_ok=True)
                imsave("img_windowed/image_{0}_/image_{0}_{1}.jpg".format(image_index, window_index), i)
                window_index = (window_index + 1) % (n_patches + 1)
                if window_index == 0:
                    print("Image and windows of index {} written on disk.".format(image_index))
                    image_index+=1



def process():
    list = get_imlist("img_cut/")

    stage1 = OrderedStage(send_batch)
    stage2 = OrderedStage(create_bag_of_window)
    stage3 = OrderedStage(last_stage)
    stage1.link(stage2)
    stage2.link(stage3)
    pipe = Pipeline(stage1)

    batch_size = 20
    total_batch = math.ceil(len(list) / batch_size)

    for p in range(total_batch):
        v = list[p * batch_size:(p + 1) * batch_size]
        print("Batch number %s" % p)
        pipe.put(v)

    pipe.put(None)



# for result in pipe.results():
#     for im_w in result: #np.vstack((r for r in result)):
#         for im in im_w:
#             for i in im:
#                 #print("saving image_{0} window_{1}".format(image_index, window_index))
#                 pathlib.Path('img_windowed/image_{0}_'.format(image_index)).mkdir(parents=True, exist_ok=True)
#                 #pathlib.Path('img_windowed/train').mkdir(parents=True, exist_ok=True)
#                 imsave("img_windowed/image_{0}_/image_{0}_{1}.jpg".format(image_index, window_index), i)
#                 window_index = (window_index + 1) % (n_patches + 1)
#                 if window_index == 0:
#                     print("Image and windows of index {} written on disk.".format(image_index))
#                     image_index+=1

t1 = time.time()
process()
print("TOTAL TIME TO PREPROCESS DATASET= {}".format(time.time() - t1))