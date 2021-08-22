import os
import json
import copy
from service.k8s_data_template_matching import K8sDataTemplateMatching

"""
数据扩充：补足k8s data中缺失的相关信息
"""


class K8sDataExpansion:
    def __init__(self):
        pass

    '''
    添加sdre容器组件
    输入:
        result_dict: {
            "nodes": OrderedDict(),
            "links": OrderedDict()
        }
    输出:
        添加了sdre组件的result_dict
    '''
    @staticmethod
    def add_sdre_component(result_dict):
        added_result_dict = copy.deepcopy(result_dict)
        for container_node in result_dict["nodes"]["container"]:
            if "carts" in container_node["name"]:
                added_result_dict = K8sDataExpansion.generate_component(container_node, added_result_dict, "sdre_component_priority.json", "sdre")
        return added_result_dict

    '''
        添加业务容器组件（SDR点对点通信丢包）
        输入:
            result_dict: {
                "nodes": OrderedDict(),
                "links": OrderedDict()
            }
        输出:
            添加了业务容器组件的result_dict
        '''

    @staticmethod
    def add_business_component(result_dict):
        added_result_dict = copy.deepcopy(result_dict)
        for container_node in result_dict["nodes"]["container"]:
            if "carts" in container_node["name"]:
                added_result_dict = K8sDataExpansion.generate_component(container_node, added_result_dict,
                                                                        "business_component_priority.json", "sdr_p2p_networking_loss")
        return added_result_dict

    @staticmethod
    def mock_vusn_service(result_dict):
        for node in result_dict["nodes"]["deployment"]:
            if "vusn-pod" in node["name"]:
                vusn_service_node = K8sDataExpansion.get_service_json_data("vusn_service.json")
                vusn_service_node["stime"] = node["stime"]
                vusn_service_node["etime"] = node["etime"]
                if "service" not in result_dict["nodes"].keys():
                    result_dict["nodes"]["service"] = []
                result_dict["nodes"]["service"].append(vusn_service_node)
                if "provides" not in result_dict["links"].keys():
                    result_dict["links"]["provides"] = []
                result_dict["links"]["provides"].append(K8sDataTemplateMatching.establish_link("provides",
                    node["id"], vusn_service_node["id"], node["stime"], node["etime"]))

                id_list = [node["id"]]
                for node_id in id_list:
                    for link_type in result_dict["links"].keys():
                        for link in result_dict["links"][link_type]:
                            if node_id == link["tid"]:
                                id_list.append(link["sid"])
                            elif node_id == link["sid"]:
                                id_list.append(link["tid"])

                break
        return result_dict

    @staticmethod
    def generate_component(container_node, result_dict, component_type, scene):
        component_priority_dict = K8sDataExpansion.get_component_json_data(component_type)
        component_template_dict = K8sDataExpansion.get_component_json_data("component.json")
        for key, value in component_priority_dict.items():
            temp_component = copy.deepcopy(component_template_dict)
            temp_component["id"] = container_node["id"] + "-" + key
            temp_component["name"] = key
            temp_component["stime"] = container_node["stime"]
            temp_component["etime"] = container_node["etime"]
            temp_component["property"]["query"]["resource"]["namespace"] = container_node["property"]["query"]["resource"]["namespace"]
            temp_component["property"]["query"]["resource"]["serviceName"] = container_node["property"]["query"]["resource"]["serviceName"]
            temp_component["property"]["query"]["resource"]["podName"] = container_node["property"]["query"]["resource"]["podName"]
            temp_component["property"]["query"]["resource"]["containerId"] = container_node["property"]["query"]["resource"]["containerId"]
            temp_component["property"]["query"]["resource"]["componentName"] = key
            temp_component["property"]["query"]["resource"]["priority"] = value

            ip_port = "10.60.38.173:5000"
            metrics_address = ip_port + "/metrics"
            logging_address = ""
            if scene == "sdr_p2p_networking_loss":
                logging_address = ip_port + "/sdr_p2p_network_loss_logging"
            elif scene == "sdre":
                logging_address = ip_port + "/sdre_reset_logging"

            params_template = {
                "resource": {
                    "namespace": container_node["property"]["query"]["resource"]["namespace"],
                    "serviceName": container_node["property"]["query"]["resource"]["serviceName"],
                    "podName": container_node["property"]["query"]["resource"]["podName"],
                    "containerId": container_node["property"]["query"]["resource"]["containerId"],
                    "componentName": key
                },
                "resource_type": "component"
            }

            query_type_list = ["query", "query_range"]
            property_type_list = ["business", "traffic"]

            for query_type in query_type_list:
                for property_type in property_type_list:
                    for property_name in temp_component["property"][query_type][property_type].keys():
                        address = ""
                        if temp_component["property"][query_type][property_type][property_name]["property-type"] == "logging":
                            address = logging_address
                        elif temp_component["property"][query_type][property_type][property_name]["property-type"] == "metrics":
                            address = metrics_address
                        else:
                            break

                        temp_component["property"][query_type][property_type][property_name][
                            "property-query-address"] = address + \
                                                        temp_component["property"][query_type][property_type][property_name][
                                                            "property-query-address"]
                        params = copy.deepcopy(params_template)
                        params["property-name"] = property_name.split("(")[0]
                        if "resource" in temp_component["property"][query_type][property_type][property_name][
                            "property-query-params"].keys():
                            params["resource"].update(temp_component["property"][query_type][property_type][property_name]["property-query-params"]["resource"])
                        temp_component["property"][query_type][property_type][property_name][
                            "property-query-params"] = params

            if "component" not in result_dict["nodes"].keys():
                result_dict["nodes"]["component"] = []
            result_dict["nodes"]["component"].append(temp_component)
            if "is_composed_of" not in result_dict["links"].keys():
                result_dict["links"]["is_composed_of"] = []
            result_dict["links"]["is_composed_of"].append(K8sDataTemplateMatching.establish_link("is_composed_of",
                    temp_component["id"], container_node["id"], container_node["stime"], container_node["etime"]))

        return result_dict

    @staticmethod
    def get_component_json_data(file):
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        template_base_path = os.path.join(current_path, 'template')
        template_base_path = os.path.join(template_base_path, 'k8s')
        template_base_path = os.path.join(template_base_path, 'component')
        if not os.path.exists(template_base_path):
            print("Invalid expansion template url: " + template_base_path)
            return ""
        json_result = dict()
        with open(os.path.join(template_base_path, file), 'r') as f:
            json_result = json.load(f)
        return json_result

    @staticmethod
    def get_service_json_data(file):
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        template_base_path = os.path.join(current_path, 'template')
        template_base_path = os.path.join(template_base_path, 'k8s')
        if not os.path.exists(template_base_path):
            print("Invalid expansion template url: " + template_base_path)
            return ""
        json_result = dict()
        with open(os.path.join(template_base_path, file), 'r') as f:
            json_result = json.load(f)
        return json_result
