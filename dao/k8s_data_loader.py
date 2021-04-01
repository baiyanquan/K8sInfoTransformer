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

        resource_type_list = ConfigLoader.load_resource_config()

        result = OrderedDict()

        if not os.path.exists(template_data_base_path):
            print("Wrong template data url!")
            return result

        for resource_type in resource_type_list["global_resource"]["resource_type"]:
            result[resource_type] = []

        for namespace in resource_type_list["local_resource"]["namespace"]:
            for resource_type in resource_type_list["local_resource"]["resource_type"]:
                result[namespace + '__' + resource_type] = []

        for k8s_data_file in os.listdir(template_data_base_path):
            for resource_type in result.keys():
                if resource_type + ".json" in k8s_data_file:
                    k8s_data_file_path = os.path.join(template_data_base_path, k8s_data_file)
                    if os.path.isdir(k8s_data_file_path):
                        print("Cannot parse directory in k8s templates!")
                        continue
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
                        deep_copy = json_data["items"].copy()
                        result[resource_type].extend(deep_copy)
                    else:
                        print("Invalid k8s information items!")
                else:
                    continue
        return result

    @staticmethod
    def get_base_path(simplified_time):
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        template_data_base_path = os.path.join(current_path, 'template_data')
        return os.path.join(template_data_base_path, 'k8s' + '_' + simplified_time)
