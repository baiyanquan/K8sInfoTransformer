import os
import json


class K8sDataWriter:
    def __init__(self):
        pass

    @staticmethod
    def write_json_data(simplified_time, json_result):
        result_base_path = K8sDataWriter.get_base_path(simplified_time)
        for key, item in json_result.items():
            json.dump(item, open(os.path.join(result_base_path, key + '.json'), 'w'), indent=4)

    @staticmethod
    def get_base_path(simplified_time):
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        result_base_path = os.path.join(current_path, 'template_data')
        result_base_path = os.path.join(result_base_path, 'k8s' + '_' + simplified_time)
        if not os.path.exists(result_base_path):
            os.makedirs(result_base_path)
        return result_base_path
