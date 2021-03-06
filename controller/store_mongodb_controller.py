from flask import Flask, jsonify, abort, request
import time
from service.k8s_data_transformer import K8sDataTransformer

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def hello():
    return 'hello'


@app.route('/store_mongodb', methods=['GET'])
def get_json():
    time.time()
    # 本地时间
    # simplified_time = time.strftime("%Y%m%d_%H%M%S")
    simplified_time = "20210314_111500"
    print(simplified_time)
    k8s_data_transformer = K8sDataTransformer()
    return k8s_data_transformer.transform_k8s_data(simplified_time)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5050', debug=True)
