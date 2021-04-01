from utils.utils import Utils
from config.config_loader import ConfigLoader
from dao.k8s_data_writer import K8sDataWriter


class K8sObserver:
    def __init__(self):
        pass

    @staticmethod
    def generate_query_cmd():
        resource_config = ConfigLoader.load_resource_config()

        cmd_dict = dict()
        for resource_type in resource_config["global_resource"]["resource_type"]:
            cmd_dict[resource_type] = resource_config["get_info_cmd"]["general"][0] + resource_type + resource_config["get_info_cmd"]["format"][0]

        for resource_type in resource_config["local_resource"]["resource_type"]:
            for namespace in resource_config["local_resource"]["namespace"]:
                cmd_dict[namespace + "__" + resource_type] = resource_config["get_info_cmd"]["general"][0] + resource_type + " -n " + namespace + resource_config["get_info_cmd"]["format"][0]
        return cmd_dict

    @staticmethod
    def exec_cmd(cmd_dict):
        resource_config = ConfigLoader.load_resource_config()

        result = dict()
        for cmd_key, cmd_value in cmd_dict.items():
            temp = Utils.verification_ssh(resource_config["k8s_config"]["host"][0], resource_config["k8s_config"]["username"][0],
                                          resource_config["k8s_config"]["password"][0], resource_config["k8s_config"]["port"][0],
                                          resource_config["k8s_config"]["password"][0], cmd_value)
            if isinstance(temp, bytes):
                temp = temp.decode("utf-8")
            result[cmd_key] = temp
        return result

    @staticmethod
    def get_k8s_info(simplified_time):
        K8sDataWriter.write_json_data(simplified_time, K8sObserver.exec_cmd(K8sObserver.generate_query_cmd()))
