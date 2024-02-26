from elasticsearch import Elasticsearch
import os
from configparser import SafeConfigParser
from elasticsearch_dsl import Search

def get_config_value(module, variable):
    _curr_path = os.getcwd()
    _config_path = os.path.join(_curr_path, './config.ini')
    _conf_value = None
    try:
        # Đọc cấu hình config của máy chủ gồm: host của elasticsearch
        _parser = SafeConfigParser()
        print(_config_path)
        _parser.read(_config_path)
        _conf_value = _parser.get(module, variable)
    except Exception as e:
        print(str(e))
    finally:
        return _conf_value

# Kết nối elasticsearch
def connect_elasticsearch():
    # Cài đặt một số cấu hình liên quan
    _es_config = get_config_value('elastic', 'es_host')
    _es_hosts = [_es_config]
    timeout = 1000
    #

    _obj_es = Elasticsearch(hosts=_es_hosts,
                            timeout=timeout)
    try:
        if _obj_es.ping():
            print('Elasticsearch is connected.')
        else:
            raise  Exception
    except  Exception as err:
        print(err)
    return _obj_es


class DATABASE:
    def __init__(self):
        # Khởi tạo server chứa toàn bộ data
        self.base = connect_elasticsearch()

    def create_index(self, site):
        # Tạo 1 index mới
        index_mapping = {
                        "mappings": {
                            "properties": {
                                "feature_vector": {
                                    "type": "dense_vector",
                                    "dims": 1000
                                }
                            }
                        },
                        "settings": {
                            "number_of_shards":5
                        }
                    }
        try:
            self.base.indices.create(index=site,
                                     body=index_mapping)
        except Exception as err:
            print(err)
        except Exception as err:
            print(f"Not create index for site {site}.")

    def get_all_index(self):
        # Lấy toàn bộ index ở trong elasticsearch
        return self.base.indices.get_alias().keys()

    # Trả về số lượng index có trong server
    def __len__(self):
        return self.len_index

    def delete_index(self, site):
        # Xóa đi index
        try:
            all_indices = self.base.indices.get_alias().keys()
            if site in all_indices:
                self.base.indices.delete(index=site,
                                         ignore=[400, 404])
        except Exception as err:
            print(err)
        except Exception as err:
            print(f"Not delete index for site {site}.")


    def create_document(self, site: str, document_id: str, id_image: str, feature_vector):
        # Tạo mới document trong index của elasticsearch
        
        doc = {
            'id_image': id_image,
            'feature_vector': feature_vector.tolist()
        }
        try:
            self.base.index(index=site, id=document_id, body=doc)
        except Exception as err:
            print(f"Not create {id_document} document.")
            print('err:', err)
        except Exception as err:
            print(err)

    def get_document(self, site: str, id_document):
        # Lấy thông tin dựa vào id trong index của elasticsearch
        return self.base.get(index=site, id=id_document)
    
    def get_all_document(self, site:str):
        #lấy thông tin toàn bộ document trong index của elasticsearch
        return self.base.search(index=site, body={"query":{"match_all":{}}})
        
    def count_document(self, site:str):
        # đếm số document nếu nó > 10000
        query = {
            "query": {
                "match_all": {}
            }
        }
        response = self.base.count(index=site, body=query)
        count = response['count']
        return count
    
    def search_similarity(self, site, vector_new):
        search_body = {
                        "query": {
                            "script_score": {
                                "query": {
                                    "match_all": {}
                                },
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'feature_vector') + 1.0",
                                    "params": {
                                        "query_vector": vector_new.tolist()
                                    }
                                }
                            }
                        }
                    }

        try:
            respone = self.base.search(index=site, body=search_body)
        except Exception as err:
            respone = 0
            print('err:', err)
        return respone
  
    def delete_document(self, site: str, id_document: str):
        try:
            all_indices = self.base.indices.get_alias().keys()
            if site in all_indices:
                self.base.delete(index=site,
                                        id=id_document)
        except Exception as err:
            print(f"Not delete {id_document} document")
        except Exception as err:
            print(err)

    def get_infor_cluster(self):
        # lấy thông tin về cụm
        return self.base.cat.shards(format="json")
        
    def fix_cluster_max(self):
        #tang so luong phan doan toi da
        settings = {
            "persistent": {
            "cluster.max_shards_per_node": "3000"
                    }
            }

        response =self.base.cluster.put_settings(body=settings)

        # Check if the request was successful
        if response.get("acknowledged"):
            print("Maximum shards per node limit updated successfully.")
        else:
            print("Failed to update the maximum shards per node limit.")
