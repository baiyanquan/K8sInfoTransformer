from flask import Flask, jsonify, abort, request
from service.k8s_data_transformer import K8sDataTransformer
import json
import  time
from flask_pymongo import PyMongo


app = Flask(__name__)

mongo=PyMongo(app,uri="mongodb://mongoadmin:mongoadmin@10.60.38.173:27017/templatedata?authSource=admin")

@app.route('/store_data', methods=['GET'])
def check():
    simplified_time = "20210215_155600"
    k8s_data_transformer = K8sDataTransformer()
    res = json.dumps(k8s_data_transformer.transform_k8s_data(simplified_time))
    data = json.loads(res)
    mongo.db.test1.insert(data)
    return res


@app.route('/get_json', methods=['GET'])
def get_tasks():
    time.time()
    # simplified_time = time.strftime("%Y%m%d_%H%M%S")
    simplified_time = "20210314_111500"
    print(simplified_time)
    k8s_data_transformer = K8sDataTransformer()
    return k8s_data_transformer.transform_k8s_data(simplified_time)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='23', debug=True)
