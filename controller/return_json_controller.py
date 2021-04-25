from flask import Flask, jsonify, abort, request
from service.k8s_data_transformer import K8sDataTransformer
import json
import  time
from flask_pymongo import PyMongo


app = Flask(__name__)


mongo = PyMongo(app,uri="mongodb://mongoadmin:mongoadmin@10.60.38.173:27017/templatedata?authSource=admin")


@app.route('/store_data', methods=['GET'])
def check():
    simplified_time = "20210215_155600"
    k8s_data_transformer = K8sDataTransformer()
    res = json.dumps(k8s_data_transformer.transform_k8s_data(simplified_time))
    data = json.loads(res)
    mongo.db.test1.insert(data)
    return res


# param: time, %Y%m%d_%H%M%S, or 20210314_111500
@app.route('/get_json', methods=['GET'])
def get_json():
    time_str = request.args.get("time")
    param = ""
    if time_str is not None:
        time_spl = time_str.split("_")
        if len(time_spl) != 2:
            return "wrong format"
        date_spl = time_spl[0].split("-")
        if len(date_spl) == 1:  # 传入的是简化版时间
            param = time_str
        else:
            clock_spl = time_spl[1].split("-")
            param = date_spl[0] + date_spl[1] + date_spl[2] + clock_spl[0] + clock_spl[1] + clock_spl[2]
    else:  # 无传入时间，获取本地时间
        time.time()
        param = time.strftime("%Y%m%d_%H%M%S")
        # simplified_time = "20210314_111500"
        # print(simplified_time)
    k8s_data_transformer = K8sDataTransformer()
    return k8s_data_transformer.transform_k8s_data(param)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='23', debug=True)
