# -*- coding: utf-8 -*-
# Author: yongyuan.name
import sys, os
import numpy as np
from numpy import linalg as LA
from keras import Model
from keras import backend as K
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions
import execnet

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from yael_wrapper import process_desc

'''
 Use vgg16 model to extract features
 Output normalized feature vector
'''
def get_tags(input):
    tags_matrix = []
    predictions_tensor = decode_predictions(input)
    for img in predictions_tensor:
        tags = []
        for prediction in img:
            id, name, odd = prediction
            if odd > 0.25:
                tags.append(name)
        tags_matrix.append(tags)
    return tags_matrix


def extract_feat_CNN(img_path):
    # weights: 'imagenet'
    # pooling: 'max' or 'avg'
    # input_shape: (width, height, 3), width and height should >= 48

    input_shape = (224, 224, 3)

    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=False)

    model.summary()

    img = image.load_img(img_path, target_size=(input_shape[0], input_shape[1]))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    feat = model.predict(img)
    norm_feat = feat[0] / LA.norm(feat[0])

    use_fv_processing = False

    if use_fv_processing:
        norm_feat = process_desc(norm_feat)

    # K.clear_session()
    return norm_feat


def extract_feat_FCL(img_path):
    # weights: 'imagenet'
    # pooling: 'max' or 'avg'
    # input_shape: (width, height, 3), width and height should >= 48

    input_shape = (224, 224, 3)

    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=True)

    img = image.load_img(img_path, target_size=(input_shape[0], input_shape[1]))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    layer_name = "fc2"
    intermediate_layer_model = Model(inputs=model.input,
                                     outputs=model.get_layer(layer_name).output)
    feat = intermediate_layer_model.predict(img)
    predictions = model.predict(img)
    tags_matrix = get_tags(predictions)

    #norm_feat = feat[0] / LA.norm(feat[0])

    # K.clear_session()
    use_fv_processing = True

    #if use_fv_processing:
    #    norm_feat = process_desc(norm_feat)


    return feat, tags_matrix[0]
