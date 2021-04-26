from flask import Flask, jsonify, abort, request
from service.k8s_data_transformer import K8sDataTransformer
import json
import  time
from flask_pymongo import PyMongo


app = Flask(__name__)


mongo = PyMongo(app,uri="mongodb://mongoadmin:mongoadmin@10.60.38.173:27017/templatedata?authSource=admin")



def read_dict(dict_str,key):
    for k, v in dict_str.items():
        if k == key:
            return v
        if type(v) is dict:
            return read_dict(v,key)

    return "在dic()里面未发现目标key"

@app.route('/store_data', methods=['GET'])
def check():
    # 默认返回内容
    return_dict = {'return_code': '200', 'return_info': '处理成功', 'result': None}
    # 判断入参是否为空
    time_str = request.args.get("time")
    simplified_time=""
    if len(request.args) == 0:
        # return_dict['return_code'] = '5004'
        # return_dict['return_info'] = '请求参数为空'
        # return json.dumps(return_dict, ensure_ascii=False)
        time.time()
        simplified_time = time.strftime("%Y%m%d_%H%M%S")
    else:
        time_spl = time_str.split("_")
        if len(time_spl) != 2:
            return "wrong format"
        date_spl = time_spl[0].split("-")
        if len(date_spl) == 1:
            simplified_time = time_str
        else:
            clock_spl = time_spl[1].split(":")
            simplified_time = date_spl[0] + date_spl[1] + date_spl[2] + clock_spl[0] + clock_spl[1] + clock_spl[2]
    k8s_data_transformer = K8sDataTransformer()
    #get_data=request.args.to_dict()
    #simplified_time = get_data.get('time')
    res=k8s_data_transformer.transform_k8s_data(simplified_time)
    k8s_data = K8sDataLoader.load_k8s_data(simplified_time)
    nodes=json.dumps(read_dict(res,"nodes"))
    links=json.dumps(read_dict(res,"links"))
    links='{"'+"_id"+'":'+'"'+simplified_time+'",'+'"'+"links"+'":'+links+'}'
    nodes='{"'+"_id"+'":'+'"'+simplified_time+'",'+'"'+"nodes"+'":'+nodes+'}'
    nodes=json.loads(nodes)
    links=json.loads(links)
    mongo.db.test1.insert(nodes)
    #mongo.db.test2.insert(k8s_data)
    mongo.db.test3.insert(links)
    return k8s_data



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
            clock_spl = time_spl[1].split(":")
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
