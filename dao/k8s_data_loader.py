import yaml
import os
import json
from collections import OrderedDict
from config.config_loader import ConfigLoader


class K8sDataLoader:
    def __init__(self):
        pass

    @staticmethod
    def load_k8s_data(simplified_time):
        # simplified_time format: "20210216_163100"
        template_data_base_path = K8sDataLoader.get_base_path(simplified_time)

        config_loader = ConfigLoader()

        resource_file_dict = config_loader.get_resource_file()

        result = OrderedDict()

        for resource_type in resource_file_dict.keys():
            result[resource_type] = dict()

        for resource_type, resource_file in resource_file_dict.items():
            k8s_data_file_path = os.path.join(template_data_base_path, resource_file)
            if os.path.exists(k8s_data_file_path):
                json_data = dict()
                with open(k8s_data_file_path) as f:
                    data = f.read()
                    if data[0] == '"':
                        data = data.strip('"')
                        # replace('\\\\\\"', '\\\\"')
                        data = data.replace('\\"', '\"').replace('\\n', '\n').replace('\\\\"', '\\"')
                    json_data = json.loads(data)
                    f.close()
                if isinstance(json_data, dict) and "items" in json_data.keys() and isinstance(json_data["items"], list):
                    deep_copy = json_data.copy()
                    result[resource_type] = deep_copy
                else:
                    print("Invalid k8s information items!")
            else:
                print("Invalid path " + str(k8s_data_file_path))
                continue

        return result

    @staticmethod
    def get_base_path(simplified_time):
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        template_data_base_path = os.path.join(current_path, 'template_data')
        template_data_base_path = os.path.join(template_data_base_path, 'k8s' + '_' + simplified_time)
        if not os.path.exists(template_data_base_path):
            print("Invalid template data url: " + template_data_base_path)
            return ""
        return template_data_base_path
