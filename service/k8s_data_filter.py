from collections import OrderedDict

"""
按照一定规则筛选实体、关系
"""


class K8sDataFilter:
    def __init__(self):
        pass

    @staticmethod
    def sdr_reset_filter(result_dict):
        # rule_list = [{
        #     "resource_type": "pod",
        #     "name": "vusn-pod"
        # }]

        rule_list = [{
            "resource_type": "pod",
            "name": "carts-74778887d9-xt6ts"
        }]

        return K8sDataFilter.relative_resource_filter(rule_list, result_dict)

    @staticmethod
    def sdr_p2p_network_loss_filter(result_dict):
        rule_list = [{
            "resource_type": "pod",
            "name": "vusn-pod"
        }, {
            "resource_type": "pod",
            "name": "comtest-pod"
        }, {
            "resource_type": "service",
            "name": "comtest-pod"
        }]

        return K8sDataFilter.relative_resource_filter(rule_list, result_dict)

    """
    筛选遵循规则的实体、关系
    输入:
        rule_list: 规则列表
        result_dict: {
            "nodes": OrderedDict(),
            "links": OrderedDict()
        }
    """
    @staticmethod
    def relative_resource_filter(rule_list, result_dict):
        filtered_result_dict = {
            "nodes": OrderedDict(),
            "links": OrderedDict(),
        }
        temp_node_list = []
        for rule in rule_list:
            for node in result_dict["nodes"][rule["resource_type"]]:
                if rule["resource_type"] not in filtered_result_dict["nodes"].keys():
                    filtered_result_dict["nodes"][rule["resource_type"]] = []
                flag = True
                for key, value in rule.items():
                    if key != "resource_type":
                        if value not in node[key]:
                            flag = False
                            break
                if flag:
                    insert = True
                    for existing_node in filtered_result_dict["nodes"][rule["resource_type"]]:
                        if existing_node["id"] == node["id"]:
                            insert = False
                            break
                    if insert:
                        filtered_result_dict["nodes"][rule["resource_type"]].append(node)
                        temp_node_list.append(node)
        length = len(temp_node_list)
        i = 0
        temp_available_link = []
        for key, value in result_dict["links"].items():
            temp_available_link.extend(value)
        while i < length:
            temp_link = temp_available_link
            for link in temp_link:
                target_node = ""
                if link["tid"] == temp_node_list[i]["id"]:
                    target_node = K8sDataFilter.find_node_by_id(link["sid"], result_dict)
                elif link["sid"] == temp_node_list[i]["id"]:
                    target_node = K8sDataFilter.find_node_by_id(link["tid"], result_dict)
                else:
                    continue

                insert = True
                for existing_node in temp_node_list:
                    if existing_node["id"] == target_node["id"]:
                        insert = False
                        break
                if insert:
                    if target_node["label"].lower() not in filtered_result_dict["nodes"].keys():
                        filtered_result_dict["nodes"][target_node["label"].lower()] = []
                    filtered_result_dict["nodes"][target_node["label"].lower()].append(target_node)
                    temp_node_list.append(target_node)

                if link["label"] not in filtered_result_dict["links"].keys():
                    filtered_result_dict["links"][link["label"]] = []
                filtered_result_dict["links"][link["label"]].append(link)
            i += 1
        return filtered_result_dict

    @staticmethod
    def find_node_by_id(node_id, result_dict):
        for key, value in result_dict["nodes"].items():
            for node in value:
                if node["id"] == node_id:
                    return node
