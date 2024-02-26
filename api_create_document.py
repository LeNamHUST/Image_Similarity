from flask import Flask, request
from create_document import add_data
from image_similarity import load_model
import os
import re
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
        
model = load_model(model_name = 'resnet50', include_top=True)

app = Flask(__name__)

@app.route('/create_vector', methods=['GET', 'POST'])
def create_vector():
    data_body = dict(request.form)
    print(data_body)
    message = 'không load được tất cả ảnh'
    if not os.path.exists('./folder_vector'):
        os.mkdir('./folder_vector')
    folder_vector = './folder_vector'
    print('tao xong folder')
    result = []
    try:
        site = data_body['site']
        user_id = data_body['user_id']
        list_image = request.values['list_image']
        list_image = list_image.split(',')
        print('list_image:', list_image)
        if not os.path.exists('./folder_vector/'+site+'_'+user_id):
            os.mkdir('./folder_vector/'+site+'_'+user_id)
        folder_user = './folder_vector/'+site+'_'+user_id
        print('folder_user:', folder_user)
        for image in list_image:
            link_img = image.split('/')
            extension_image = os.path.splitext(image)[1]
            try:
                img_path = urllib.request.urlretrieve(image, folder_user + '/' + link_img[-1])
                img_ = cv2.imread(img_path[0])
                plt.imshow(img_)
                document_id = user_id + '_' + link_img[-1]
                add_data(site, document_id, img_path[0], image, model)
                del img_path
                del img_
                del document_id
            except Exception as err:
                message = 'không load được ảnh {}'.format(image)
                error = ErrorModel(200, message)
            del image
        del list_image
        message = 'luu thanh cong'
        result = 1
        data = DataModel(True, message, result)
        print(result)
        error = None
    except Exception as err:
        print('err:', err)
        data = None
        error = ErrorModel(200, message)
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)

    response = ResponseModel(data, error)
    return json.dumps(vars(response))


if __name__=='__main__':
    app.run(debug=False, host='43.239.223.137', port=8025)