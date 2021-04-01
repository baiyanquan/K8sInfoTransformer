import os
import json


class JsonResultWriter:
    def __init__(self):
        pass

    @staticmethod
    def write_json_data(simplified_time, json_result):
        result_base_path = JsonResultWriter.get_base_path(simplified_time)
        node_result = {"data": json_result["nodes"]}
        link_result = {"data": json_result["links"]}
        json.dump(node_result, open(os.path.join(result_base_path, 'nodesnew.json'), 'w'), indent=4)
        json.dump(link_result, open(os.path.join(result_base_path, 'linksnew.json'), 'w'), indent=4)

    @staticmethod
    def get_base_path(simplified_time):
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        result_base_path = os.path.join(current_path, 'json_result')
        result_base_path = os.path.join(result_base_path, 'k8s' + '_' + simplified_time)
        if not os.path.exists(result_base_path):
            os.makedirs(result_base_path)
        return result_base_path
