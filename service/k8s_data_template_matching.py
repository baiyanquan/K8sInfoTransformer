from collections import OrderedDict
import copy
from utils.utils import Utils


class K8sDataTemplateMatching:
    def __init__(self):
        pass

    '''
    模板匹配函数: 将原始的k8s数据与模板进行匹配
    输入:
        k8s_data_dict: key为资源类别，value为原始资源信息的dict;
        parse_template_dict: key为资源类别，value为模板信息的dict;
    输出：
        {
            "nodes": {
                "service": [],
                "pod": [],
                ...
            }
            "links": [...]
        }
    '''
    @staticmethod
    def template_matching(k8s_data_dict, parse_template_dict, global_env_dict, etime):
        result_dict = {
            "nodes": OrderedDict(),
            "links": OrderedDict()
        }

        for resource_type, resource_data in k8s_data_dict.items():
            if resource_type in parse_template_dict.keys():
                result_dict["nodes"][resource_type] = []

                # 1. 解析info_position，获取数据位置，放到item_list中
                template_info_position_list = parse_template_dict[resource_type]["info_position"]
                #    数据源描述的主体是当前实体，不存在复合情况
                if isinstance(template_info_position_list, list) and len(template_info_position_list) == 1:
                    item_list = []
                    for index in str(template_info_position_list[0]).split("///"):
                        item_list = k8s_data_dict[resource_type][index]
                    for item in item_list:
                        # 2. 解析env，将本地的环境变量与全局环境变量复合
                        env_dict = copy.deepcopy(global_env_dict)
                        if isinstance(parse_template_dict[resource_type]["env"], dict):
                            for key, value in parse_template_dict[resource_type]["env"].items():
                                env_dict[key] = K8sDataTemplateMatching.parse_property(key, value, item, global_env_dict)

                        temp_node = {
                            "id": K8sDataTemplateMatching.parse_property(
                                "id", parse_template_dict[resource_type]["base"]["id"], item, env_dict),
                            "stime": K8sDataTemplateMatching.parse_property(
                                "stime", parse_template_dict[resource_type]["base"]["stime"], item, env_dict),
                            "etime": etime
                        }
                        # 3. 解析relationship
                        if "relationship" in parse_template_dict[resource_type]:
                            for relationship_name, relationship_template_dict in parse_template_dict[resource_type]["relationship"].items():
                                links_dict = K8sDataTemplateMatching.parse_relationship(
                                    relationship_name, relationship_template_dict, result_dict, temp_node, item, env_dict)
                                for key, value in links_dict.items():
                                    if key not in result_dict["links"].keys():
                                        result_dict["links"][key] = value
                                    else:
                                        result_dict["links"][key].extend(value)

                        # 4. 解析base
                        #    最终生成的node
                        node = OrderedDict()
                        for key, value in parse_template_dict[resource_type]["base"].items():
                            if value["property-type"] == "connector":
                                node[key] = K8sDataTemplateMatching.parse_connector_property(value, result_dict, temp_node, parse_template_dict[resource_type]["relationship"][value["relation-kind"]]["entity-type"])
                            else:
                                node[key] = K8sDataTemplateMatching.parse_property(key, value, item, env_dict)
                        node["etime"] = etime
                        node["property"] = OrderedDict()

                        # 5. 解析property
                        for query_type, query_dict in parse_template_dict[resource_type]["property"].items():
                            if query_type not in node["property"].keys():
                                node["property"][query_type] = dict()
                            for query_property_kind, query_property_dict in query_dict.items():
                                if query_property_kind not in node["property"][query_type].keys():
                                    node["property"][query_type][query_property_kind] = dict()
                                for property_name, property_dict in query_property_dict.items():
                                    if property_name == "networkTransmitted":
                                        print(property_dict["property-query-address"])
                                        pass
                                    if property_dict["property-type"] == "connector":
                                        node["property"][query_type][query_property_kind][property_name] = K8sDataTemplateMatching.parse_connector_property(property_dict, result_dict, temp_node, parse_template_dict[resource_type]["relationship"][property_dict["relation-kind"]]["entity-type"])
                                    else:
                                        node["property"][query_type][query_property_kind][property_name] = K8sDataTemplateMatching.parse_property(property_name, property_dict.copy(), item, env_dict)

                        result_dict["nodes"][resource_type].append(node)

                #    数据源描述的主体不是当前实体，存在复合情况（Container）
                elif isinstance(template_info_position_list, list) and len(template_info_position_list) == 2:
                    father_item_list = []
                    for index in str(template_info_position_list[0]).split("///"):
                        father_item_list = k8s_data_dict[resource_type][index]
                    for father_item in father_item_list:
                        item_list = father_item
                        for index in str(template_info_position_list[1]).split("///"):
                            item_list = item_list[index]
                        for item in item_list:
                            # 2. 解析env，将本地的环境变量与全局环境变量复合
                            env_dict = copy.deepcopy(global_env_dict)
                            if isinstance(parse_template_dict[resource_type]["env"], dict):
                                for key, value in parse_template_dict[resource_type]["env"].items():
                                    env_dict[key] = K8sDataTemplateMatching.parse_property(key, value, item,
                                                                                           global_env_dict)

                            temp_node = {
                                "id": K8sDataTemplateMatching.parse_property(
                                    "id", parse_template_dict[resource_type]["base"]["id"], item, env_dict),
                                "stime": K8sDataTemplateMatching.parse_property(
                                    "stime", parse_template_dict[resource_type]["base"]["stime"], item, env_dict),
                                "etime": etime
                            }

                            # 3. 解析relationship
                            if "relationship" in parse_template_dict[resource_type]:
                                for relationship_name, relationship_template_dict in parse_template_dict[resource_type]["relationship"].items():
                                    temp_item = item
                                    temp_relationship_template_dict = copy.deepcopy(relationship_template_dict)
                                    if "...///" in relationship_template_dict["filter"]:
                                        temp_item = father_item
                                        temp_relationship_template_dict["filter"] = str(temp_relationship_template_dict["filter"]).replace("...///", "")
                                    links_dict = K8sDataTemplateMatching.parse_relationship(relationship_name,
                                                                                            temp_relationship_template_dict,
                                                                                            result_dict, temp_node,
                                                                                            temp_item, env_dict)
                                    for key, value in links_dict.items():
                                        if key not in result_dict["links"].keys():
                                            result_dict["links"][key] = value
                                        else:
                                            result_dict["links"][key].extend(value)

                            # 4. 解析base
                            #    最终生成的node
                            node = OrderedDict()
                            for key, value in parse_template_dict[resource_type]["base"].items():
                                if value["property-type"] == "connector":
                                    node[key] = K8sDataTemplateMatching.parse_connector_property(value, result_dict,
                                                temp_node, parse_template_dict[resource_type]["relationship"]
                                                [value["relation-kind"]]["entity-type"])
                                else:
                                    node[key] = K8sDataTemplateMatching.parse_property(key, value, item, env_dict)
                                    node["etime"] = etime
                            node["property"] = OrderedDict()

                            # 5. 回填环境变量
                            for key, value in parse_template_dict[resource_type]["env"].items():
                                if value["property-type"] == "connector":
                                    env_dict[key] = K8sDataTemplateMatching.parse_connector_property(
                                        value.copy(), result_dict, temp_node,
                                        parse_template_dict[resource_type]["relationship"][
                                            value["relation-kind"]]["entity-type"])

                            # 6. 解析property
                            for query_type, query_dict in parse_template_dict[resource_type]["property"].items():
                                if query_type not in node["property"].keys():
                                    node["property"][query_type] = dict()
                                for query_property_kind, query_property_dict in query_dict.items():
                                    if query_property_kind not in node["property"][query_type].keys():
                                        node["property"][query_type][query_property_kind] = dict()
                                    for property_name, property_dict in query_property_dict.items():
                                        if property_dict["property-type"] == "connector":
                                            node["property"][query_type][query_property_kind][
                                                property_name] = K8sDataTemplateMatching.parse_connector_property(
                                                property_dict.copy(), result_dict, temp_node,
                                                parse_template_dict[resource_type]["relationship"][
                                                    property_dict["relation-kind"]]["entity-type"])
                                        else:
                                            new_property = K8sDataTemplateMatching.parse_property(property_name,
                                                                                                        property_dict.copy(),
                                                                                                        item, env_dict)
                                            if isinstance(new_property, dict):
                                                node["property"][query_type][query_property_kind][
                                                    property_name] = new_property.copy()
                                            else:
                                                node["property"][query_type][query_property_kind][
                                                    property_name] = new_property

                            result_dict["nodes"][resource_type].append(node)

            else:
                print("Invalid resource " + resource_type + " in parsing template")

        return result_dict

    '''
    按照yaml中提及的方式解析除connector的属性
    '''
    @staticmethod
    def parse_property(property_name, property_template_dict, k8s_data, env_dict):
        if property_template_dict["property-type"] == "separator":
            result_dict = dict()
            for key, value in property_template_dict.items():
                if key != "property-type":
                    result_dict[key] = K8sDataTemplateMatching.parse_property(property_name, value, k8s_data, env_dict)
            return result_dict
        elif property_template_dict["property-type"] == "value":
            return K8sDataTemplateMatching.value_transform_env(property_template_dict["property-value"], env_dict)
        elif property_template_dict["property-type"] == "config":
            result = ""
            for find_str in property_template_dict["property-find-str"]:
                result = K8sDataTemplateMatching.find_str_transform_env(find_str, k8s_data, env_dict)
                if result is not None:
                    break
            if "time" in property_name:
                result = Utils.datetime_timestamp(result.replace("T", " ").replace("Z", ""))
            return result
        elif property_template_dict["property-type"] == "logging" or property_template_dict["property-type"] == "tracing" or property_template_dict["property-type"] == "metrics":
            property_template_dict["property-query-address"] = K8sDataTemplateMatching.value_transform_env(property_template_dict["property-query-address"], env_dict)
            if property_template_dict["property-query-params"] == "":
                property_template_dict["property-query-params"] = {}
            return property_template_dict.copy()
        elif property_template_dict["property-type"] == "aggregator":
            return property_template_dict
        elif property_template_dict["property-type"] == "connector":
            return ""

    '''
    解析connector属性
    '''
    @staticmethod
    def parse_connector_property(property_template_dict, result_dict, node, target_resource_type):
        result_list = []
        for link in result_dict["links"][property_template_dict["relation-kind"]]:
            target_id = ""
            if node["id"] == link["sid"]:
                target_id = link["tid"]
            elif node["id"] == link["tid"]:
                target_id = link["sid"]
            else:
                continue
            for item in result_dict["nodes"][target_resource_type]:
                if item["id"] == target_id:
                    value = item
                    index_list = property_template_dict["entity-property-find-str"].split("///")
                    for index in index_list:
                        value = value[index]
                    result_list.append(value)
        if len(result_list) == 1:
            result_list = result_list[0]
        return result_list

    @staticmethod
    def value_transform_env(value, env_dict):
        a = value
        if "$$" in str(value):
            temp_list = str(value).split("$$")
            i = 1
            while i < len(temp_list) - 1:
                temp_list[i] = env_dict[temp_list[i]]
                i += 2
            value = ''.join(temp_list)
        if "192.168.199.31" in value:
            print(a)
            print(value)
            pass
        return value

    @staticmethod
    def find_str_transform_env(value, k8s_data, env_dict):
        temp_list = str(value).split("$$")
        i = 0
        while i < len(temp_list):
            if i % 2 == 1:
                temp_list[i] = env_dict[temp_list[i]]
            else:
                temp = k8s_data
                index_list = temp_list[i].split("///")
                for index in index_list:
                    if index == "":
                        temp = ""
                        continue
                    elif index in temp.keys():
                        temp = temp[index]
                    else:
                        return None
                temp_list[i] = temp
            i += 1
        value = temp_list[0]
        for i in range(1, len(temp_list)):
            value += temp_list[i]
        return value

    '''
    解析单个关系：
    输入：
        relationship_name: relation名称
        relationship_template_dict: 解析的relation模板
        result_dict: 能够建立关系的列表，与template_matching中的结构相同
        node: 包含当前实体基本信息的node，至少有id、stime、etime
        k8s_data: 分析使用的原始k8s数据
        env_dict: 环境变量列表
    输出：
        relationship_result_dict: {
            "is_composed_of": [],
            "contains": [],
            ...
        }
    '''
    @staticmethod
    def parse_relationship(relationship_name, relationship_template_dict, result_dict, node, k8s_data, env_dict):
        relationship_result_dict = dict()

        target_resource_type = relationship_template_dict["entity-type"]

        if target_resource_type in result_dict["nodes"].keys():
            for target_item in result_dict["nodes"][target_resource_type]:
                has_link = False
                # 判断 ==== 条件：左右全部相等
                if "====" in relationship_template_dict["filter"]:
                    node_filter = K8sDataTemplateMatching.find_str_transform_env(
                        relationship_template_dict["filter"].split(" ==== ")[0], k8s_data, env_dict)
                    target_node_filter = K8sDataTemplateMatching.find_str_transform_env(
                        relationship_template_dict["filter"].split(" ==== ")[1], target_item, {})
                    if node_filter == target_node_filter:
                        has_link = True

                # 判断 <<<< 条件：当解析值为json时，左边的键值对全部包含在右边中符合条件；当解析值为字符串时，左边的字符串包含于右边中符合条件
                elif "<<<<" in relationship_template_dict["filter"]:
                    node_filter = K8sDataTemplateMatching.find_str_transform_env(
                        relationship_template_dict["filter"].split(" <<<< ")[0], k8s_data, env_dict)
                    target_node_filter = K8sDataTemplateMatching.find_str_transform_env(
                        relationship_template_dict["filter"].split(" <<<< ")[1], target_item, {})
                    if isinstance(node_filter, str) and isinstance(target_node_filter, str):
                        if node_filter in target_node_filter:
                            has_link = True
                    if isinstance(node_filter, dict) and isinstance(target_node_filter, dict):
                        if node_filter.items() <= target_node_filter.items():
                            has_link = True

                # 判断 >>>> 条件：与 <<<< 判断相反
                elif ">>>>" in relationship_template_dict["filter"]:
                    node_filter = K8sDataTemplateMatching.find_str_transform_env(
                        relationship_template_dict["filter"].split(" >>>> ")[0], k8s_data, env_dict)
                    target_node_filter = K8sDataTemplateMatching.find_str_transform_env(
                        relationship_template_dict["filter"].split(" >>>> ")[1], target_item, {})
                    if isinstance(node_filter, str) and isinstance(target_node_filter, str):
                        if target_node_filter in node_filter:
                            has_link = True
                    if isinstance(node_filter, dict) and isinstance(target_node_filter, dict):
                        if node_filter.items() >= target_node_filter.items():
                            has_link = True

                # 关系存在
                if has_link:
                    if relationship_name not in relationship_result_dict.keys():
                        relationship_result_dict[relationship_name] = []
                    # 提取关系信息
                    tid = ""
                    sid = ""
                    stime = ""
                    etime = target_item["etime"]

                    if relationship_template_dict["direction"] == "forward":
                        tid = node["id"]
                        sid = target_item["id"]
                    elif relationship_template_dict["direction"] == "reverse":
                        sid = node["id"]
                        tid = target_item["id"]

                    if node["stime"] != "":
                        stime = max(node["stime"], target_item["stime"])
                    else:
                        stime = target_item["stime"]

                    new_link = K8sDataTemplateMatching.establish_link(relationship_name, tid, sid, stime, etime)
                    relationship_result_dict[relationship_name].append(new_link)

        else:
            print("Incorrect relationship entity type " + target_resource_type + " in relationship parsing")
        return relationship_result_dict

    @staticmethod
    def establish_link(relationship_name, tid, sid, stime, etime):
        link = dict()
        link["stime"] = stime
        link["etime"] = etime
        link["name"] = relationship_name
        link["label"] = relationship_name
        link["tid"] = tid
        link["sid"] = sid
        return link
