import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial

from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.resnet50 import ResNet50
from keras.models import Model
from keras.preprocessing import image
import keras.utils as image
from keras.applications.imagenet_utils  import preprocess_input

import cv2

def load_model(model_name, include_top=True):
    available_models = ['vgg16', 'resnet50']
    if model_name in available_models:
        try:
            if model_name == 'vgg16':
                model = VGG16(weights='imagenet', include_top=include_top)
            elif model_name == 'resnet50':
                model = ResNet50(weights='imagenet', include_top=include_top)
            print(f">> '{model.name}' model successfully loaded")
        except:
            print(f">> Error while loading model'{selected_model}")
    else:
        print(f">> Error: there is no '{selected_model}' in '{availabel_models}'")
    return model

def get_img_size_model(model):
    model_name = model.name
    if model_name == 'vgg16':
        img_size_model = (224, 224)
    elif model_name =='resnet50':
        img_size_model = (224, 224)
    else:
        img_size_model = (224, 224)
        print("warning: model name unknown, default image size: .{}".format(img_size_model))
    return img_size_model

def get_layername_feature_extraction(model):
    model_name = model.name
    if model_name == 'vgg16':
        layername_feature_extraction = 'fc2'
    elif model_name == 'resnet50':
        layername_feature_extraction = 'predictions'
    else:
        layername_feature_extraction = ''
        print("warning: model name unknown, default layername: .{}".format(layername_feature_extraction))
    return layername_feature_extraction

def get_layers_list(model):
    layers_list = []
    for i in range(len(model.layers)):
        layer = model.layers[i]
        layers_list.append(layer.name)
    return layers_list

def image_processing(img_array):
    img = np.expand_dims(img_array, axis=0)
    processed_img = preprocess_input(img)
    return processed_img


def get_feature_vector(model, img_path):
    layername_feature_extraction = get_layername_feature_extraction(model)
    model_feature_vect = Model(inputs=model.input, outputs=model.get_layer(layername_feature_extraction).output)

    img_size_model = get_img_size_model(model)
    img = image.load_img(img_path, target_size=img_size_model)
    img_arr = np.array(img)
    img_pre = image_processing(img_arr)

    feature_vector = model_feature_vect.predict(img_pre)

    return feature_vector

def calculate_similarity(vector_1, vector_2):
    sim_cos = 1-spatial.distance.cosine(vector_1, vector_2)
    return sim_cos


def compute_similarity_img(model, img_path_1, img_path_2):
    vector_1 = get_feature_vector(model, img_path_1)
    vector_2 = get_feature_vector(model, img_path_2)
    vector_1 = np.squeeze(vector_1)
    vector_2 = np.squeeze(vector_2)
    sim_cos = calculate_similarity(vector_1, vector_2)

    return sim_cos

def concatenate_image(model, img_path_1, img_path_2):
    img_size_model = get_img_size_model(model)
    img1 = cv2.resize(cv2.imread(img_path_1), dsize=img_size_model)
    img2 = cv2.resize(cv2.imread(img_path_2), dsize=img_size_model)
    img12 = cv2.hconcat([img1, img2])
    return img12
'''
img_path_1 = './data_test/74.jpg'
img_path_2 = './data_test/75.jpg'
plt.imshow(cv2.imread(img_path_1))
plt.show()
plt.imshow(cv2.imread(img_path_2))
plt.show()
available_models = ['vgg16', 'resnet50']

for selected_model in available_models:
    print(selected_model)
    model = load_model(selected_model, include_top=True)
    cos = compute_similarity_img(model, img_path_1, img_path_2)
    print(cos)
    img12 = concatenate_image(model, img_path_1, img_path_2)
    plt.imshow(img12)
    plt.show()
'''
