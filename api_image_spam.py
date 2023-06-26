#####
#####
from flask import Flask, request
from image_similarity import load_model, compute_similarity_img
import os
import urllib.request
import uuid
import json
import shutil
import cv2
import matplotlib.pyplot as plt

class ErrorModel:
    def __init__(self, code, message):
        self.code = code
        self.message = message

class DataModel:
    def __init__(self, result, message, item):
        self.result = result
        self.message = message
        self.item = item

class ResponseModel:
    # Trả về phản hồi gồm data và error
    def __init__(self, data, error):
        self.data = data
        self.error = error

app = Flask(__name__)

@app.route('/image_spam', methods=['GET', 'POST'])
def image_spam():
    data_body = dict(request.form)
    print(data_body)
    message = 'không load được tất cả ảnh'
    if not os.path.exists('./folder_image'):
        os.mkdir('./folder_image')
    folder_image = './folder_image'
    result = []
    try:
        new_image = request.values['new_image']
        list_image = request.values['list_image']

        new_img_path = urllib.request.urlretrieve(new_image, folder_image + '/' + str(uuid.uuid4()) +'.png')
        new_image = new_image.split('/')
        try:
            img = cv2.imread(new_img_path[0])
            plt.imshow(img)
        except:
            data = None
            message = 'không load được ảnh {}'.format(new_image[-1])
            error = ErrorModel(200, message)

        list_image = list_image.split(',')
        for image in list_image:
            data_sim = {}
            img_path = urllib.request.urlretrieve(image, folder_image + '/' + str(uuid.uuid4()) + '.png')
            image = image.split('/')
            try:
                img_ = cv2.imread(img_path[0])
                plt.imshow(img_)
            except:
                message = 'không load được ảnh {}'.format(image[-1])
                error = ErrorModel(200, message)
                data_sim['similarity_image'] = float(0)
                data_sim['id_image'] = image[-1]
                result.append(data_sim)
                data = DataModel(True, message, result)
            model = load_model(model_name = 'resnet50', include_top=True)
            sim_cos = compute_similarity_img(model, new_img_path[0], img_path[0])
            data_sim['similarity_image'] = float(sim_cos)
            data_sim['id_image'] = image[-1]
            result.append(data_sim)
        message = 'So sánh thành công'
        data = DataModel(True, message, result)
        error = None
    except Exception as err:
        error = ErrorModel(200, message)

    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)

    shutil.rmtree(folder_image)

    response = ResponseModel(data, error)
    return json.dumps(vars(response))

if __name__=='__main__':
    app.run(debug=True, host='127.0.0.1', port=8002)