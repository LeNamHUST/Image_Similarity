from image_similarity import load_model, get_feature_vector
from server import DATABASE


_SERVER_ = DATABASE()

def add_data(index, document_id, image_path, id_image, model):
    #kiểm tra nếu index chưa có trong kho thì tạo index
    #print('all index in base:', _SERVER_.get_all_index())
    print('bắt đầu tạo document')
    if index not in _SERVER_.get_all_index():
        _SERVER_.create_index(index)
        print('đã tạo xong index: {}'.index)
    image_vector = get_feature_vector(model, image_path)
    _SERVER_.create_document(site=index,
                            document_id=document_id,
                            id_image=id_image,
                            feature_vector=image_vector[0])
    del image_vector
    return 0
