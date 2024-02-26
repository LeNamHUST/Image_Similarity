#####
#####
from server import DATABASE
from flask import Flask, request
from image_similarity import load_model, compute_similarity_img, get_feature_vector
from create_document import add_data
import os
import re
import urllib.request
import uuid
import json
import shutil
import cv2
import matplotlib.pyplot as plt
import datetime

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

_SERVER_ = DATABASE()

model = load_model(model_name = 'resnet50', include_top=True)

file_log = open("/home/duchinh/AI_365/spam_anh/spam.txt", "a")

app = Flask(__name__)

@app.route('/image_spam', methods=['GET', 'POST'])
def image_spam():
    data_body = dict(request.form)
    print(data_body)
    folder_image = '/home/duchinh/AI_365/spam_anh/folder_img/' + '_' + str(datetime.datetime.now())
    if not os.path.exists(folder_image):
        os.mkdir(folder_image)
    print('tao xong folder')
    results = []
    try:
        message = 'So sánh thành công'
        site = data_body['site']
        user_id = data_body['user_id']
        list_image = request.values['list_image']
        list_image = list_image.split(',')
        index = site
        for image in list_image:
            link_img = image.split('/')
            #link_image = image.replace('https://timviec365.vn/', '')
            #link_image = image.replace('https://raonhanh365.vn/', '')
            #if 'timviec' in link_image:
            #    link_image = link_image.split('/')[-1]
            similarity = {}
            similarity[image] = []
            extension_image = os.path.splitext(image)[1]
            document_id = user_id + '_' + link_img[-1]
            try:
                img_path = urllib.request.urlretrieve(image, folder_image + '/' + link_img[-1])
                img_ = cv2.imread(img_path[0])
                plt.imshow(img_)
            except Except as err:
                print('err:', err)
                message = 'không load được ảnh '
                error = ErrorModel(200, message)
            if index not in _SERVER_.get_all_index():
                _SERVER_.create_index(index)
                print('nếu index chưa tồn tại trong kho thì tạo index mới rồi thêm vector ảnh vào trong kho')
                try:
                    add_data(index, document_id, img_path[0], image, model)
                    #rank = {}
                    #rank['score'] = '0'
                    #print('thêm ảnh vào kho')
                    #similarity[link_img[-1]].append(rank)
                    #results.append(similarity)
                except:
                    print('ảnh lỗi k thêm được')
                    #similarity[link_img[-1]].append('-1')
                    #results.append(similarity)
            else:
                try:
                    vector_new = get_feature_vector(model, img_path[0])
                    if len((_SERVER_.get_all_document(index)['hits']['hits'])) > 0:
                        result_search = _SERVER_.search_similarity(index, vector_new[0])
                        print('lens:', len(result_search['hits']['hits']))
                        for i in range(len(result_search['hits']['hits'])):
                            rank = {}
                            if result_search['hits']['hits'][i]['_score'] >= 1.95 :
                                rank['score'] = (float(result_search['hits']['hits'][i]['_score'])-1)*100
                                id = (result_search['hits']['hits'][i]['_source']['id_image']).replace('%20', ' ')
                                file_log.write(image + '===' + id + '\n')
                                rank['id_img'] = id
                                rank['id'] = result_search['hits']['hits'][i]['_id']
                                similarity[image].append(rank)
                            if result_search['hits']['max_score'] < 1.99999:
                                #rank['score'] = '0'
                                #similarity[link_img[-1]] = ['0']
                                add_data(index, document_id, img_path[0], image, model)
                                #print('không tìm thấy vector tương đồng thì thêm vào kho')
                                message = 'So sánh thành công'
                        del result_search
                    else:
                        add_data(index, document_id, img_path[0], image, model)
                        print('trong kho không có ảnh thì không thực hiện truy vấn mà thêm vào kho')
                    unique_similarity = {}
                    unique_similarity[image] = []
                    seen_id_imgs = set()
                    id_remove = []
                    for item in similarity[image]:
                        id_img = item["id_img"]
                        id_doc = item["id"]
                        if id_img not in seen_id_imgs :
                            if user_id in id_doc:
                                unique_similarity[image].append(item)
                                seen_id_imgs.add(id_img)
                        else:
                            id_remove.append(item["id"])
                    results.append(unique_similarity)
                    if len(id_remove) > 0:
                        for idx in id_remove:
                            _SERVER_.delete_document(index, idx)
                    del unique_similarity
                    del seen_id_imgs
                    del vector_new
                    print('result:', results)
                except Exception as err:
                    print('err:', err)
            del similarity
        del list_image
        data = DataModel(True, message, results)
        error = None
    except Exception as err:
        message = 'không load được tất cả ảnh'
        data = None
        error = ErrorModel(200, message)
    if data is not None:
        data = vars(data)
    if error is not None:
        error = vars(error)

    #shutil.rmtree(folder_image)

    response = ResponseModel(data, error)
    return json.dumps(vars(response))
    
    
@app.route('/delete_document', methods=['GET', 'POST'])
def delete_document():
    data_body = dict(request.form)
    print(data_body)
    try:
        index = data_body['site']
        user_id = data_body['user_id']
        link_image = request.values['link_image']
        link_image = link_image.split('/')
        document_id = user_id + '_' + link_image[-1]
        _SERVER_.delete_document(index, document_id)
        message = 'xóa thành công'
    except Exception as err:
        print('err:', err)
        message = 'không thể xóa ảnh'
    return json.dumps(message)
    
if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=8028)