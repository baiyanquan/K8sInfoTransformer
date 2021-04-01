from dao.parse_template_loader import ParseTemplateLoader
from dao.k8s_data_loader import K8sDataLoader
from dao.json_result_writer import JsonResultWriter
from utils.utils import Utils
from collections import OrderedDict
from datetime import datetime


class K8sDataTransformer:
    def __init__(self):
        self.parse_template = dict()
        self.load_parse_template()
        self.node_dict = OrderedDict()
        self.link_list = []
        self.arg_dict = dict()
        pass

    def transform_k8s_data(self, time):
        simplified_time = str(time).replace(" ", "_").replace("-", "").replace(":", "")
        k8s_data = K8sDataLoader.load_k8s_data(simplified_time)
        for resource_type, resource_items in k8s_data.items():
            clean_resource_type = str(resource_type).split("__")[-1]
            for item in resource_items:
                self.parse_resource_item(item, self.parse_template[clean_resource_type])
        json_result = dict()
        json_result["nodes"] = []
        for key, value in self.node_dict.items():
            json_result["nodes"].extend(value)
        json_result["links"] = self.link_list

        JsonResultWriter.write_json_data(simplified_time, json_result)

        for clean_resource_type in self.parse_template.keys():
            self.arg_dict[clean_resource_type] = self.parse_template[clean_resource_type]["arg"]

    def load_parse_template(self):
        self.parse_template = ParseTemplateLoader.load_parse_template()

    def parse_resource_item(self, item, parse_template):
        node_item = dict()

        # 1. env
        env_dict = dict()
        for env_key in parse_template["env"]:
            if "///" in parse_template["env"][env_key]:
                indices = str(parse_template["env"][env_key]).split("///")[1:]
                value = item
                find_flag = True
                for index in indices:
                    if index in value:
                        value = value[index]
                    else:
                        print("Invalid index of base value:" + parse_template["env"][env_key])
                        find_flag = False
                if find_flag:
                    env_dict[env_key] = value
            else:
                env_dict[env_key] = parse_template["env"][env_key]

        # 2. base
        for base_key in parse_template["base"]:
            if "///" in str(parse_template["base"][base_key]):
                indices = str(parse_template["base"][base_key]).split("///")[1:]
                value = item
                find_flag = True
                for index in indices:
                    if index in value:
                        value = value[index]
                    else:
                        print("Invalid index of base value:" + parse_template["base"][base_key])
                        find_flag = False
                if find_flag:
                    prefix = str(parse_template["base"][base_key]).split("///")[0]
                    if "$$" in prefix:
                        prefix = env_dict[prefix.replace("$$", "")]
                    node_item[base_key] = prefix + value
                    if "time" in base_key:
                        node_item[base_key] = Utils.datetime_timestamp(node_item[base_key].replace("T", " ").replace("Z", ""))
            else:
                value = parse_template["base"][base_key]
                node_item[base_key] = self.transform_env(value, env_dict)

        # 3. property
        node_item["property"] = dict()
        # 3.1 configuration
        node_item["property"]["configuration"] = dict()
        for configuration_key in parse_template["property"]["configuration"]:
            if "///" in parse_template["property"]["configuration"][configuration_key]:
                indices = str(parse_template["property"]["configuration"][configuration_key]).split("///")[1:]
                value = item
                find_flag = True
                for index in indices:
                    if index in value:
                        value = value[index]
                    else:
                        print("Invalid index of property value:" + parse_template["property"]["configuration"][configuration_key])
                        find_flag = False
                if find_flag:
                    node_item["property"]["configuration"][configuration_key] = value
            else:
                value = parse_template["property"]["configuration"][configuration_key]
                node_item["property"]["configuration"][configuration_key] = self.transform_env(value, env_dict)
        # 3.2 query
        query_list = ["query", "query_range"]
        for query_key in query_list:
            node_item["property"][query_key] = dict()
            for property_type in parse_template["property"][query_key]:
                node_item["property"][query_key][property_type] = []
                if not isinstance(parse_template["property"][query_key][property_type], dict):
                    continue
                for query_property, details in parse_template["property"][query_key][property_type].items():
                    temp = dict()
                    if isinstance(details, dict):
                        for key, value in details.items():
                            temp[key] = self.transform_env(value, env_dict)
                    temp["name"] = query_property
                    node_item["property"][query_key][property_type].append(temp)

        # 3.3 sub_entity
        if "sub_entity" in parse_template.keys():
            indices = str(parse_template["sub_entity"]["position"]).split("///")[1:]
            value = item
            find_flag = True
            for index in indices:
                if index in value:
                    value = value[index]
                else:
                    print("Invalid index of sub_entity value:" + parse_template["sub_entity"]["position"])
                    find_flag = False
            if find_flag:
                sub_entity_list = value
                if not isinstance(sub_entity_list, list):
                    print("Invalid sub_entity_list:" + parse_template["sub_entity"][
                        "position"])
                else:
                    for sub_entity in sub_entity_list:
                        sub_entity_item = self.parse_resource_item(sub_entity, parse_template["sub_entity"])
                        self.establish_link(node_item, sub_entity_item, parse_template["sub_entity"]["sub_relationship"])

        # 4 relationship
        if "relationship" in parse_template.keys() and isinstance(parse_template["relationship"], dict):
            for relationship_name, details in parse_template["relationship"].items():
                target_entity_list = []
                constraints = dict()
                for detail_key in details.keys():
                    if detail_key == "entity_type":
                        if details[detail_key] in self.node_dict.keys():
                            target_entity_list = self.node_dict[details[detail_key]]
                        else:
                            print("Read order error")
                    else:
                        if "///" in details[detail_key]:
                            indices = str(details[detail_key]).split("///")[1:]
                            value = item
                            find_flag = True
                            for index in indices:
                                if index in value:
                                    value = value[index]
                                else:
                                    print("Invalid index of relationship value:" + details[detail_key])
                                    find_flag = False
                            if find_flag:
                                prefix = str(details[detail_key]).split("///")[0]
                                if "$$" in prefix:
                                    prefix = env_dict[prefix.replace("$$", "")]
                                constraints[detail_key] = prefix + value
                        else:
                            value = details[detail_key]
                            constraints[detail_key] = self.transform_env(value, env_dict)
                pass
                for entity in target_entity_list:
                    target = True
                    for key, constraint_value in constraints.items():
                        indices = key.split("///")[1:]
                        value = entity
                        find_flag = True
                        for index in indices:
                            if index in value:
                                value = value[index]
                            else:
                                print("Invalid relationship index in target entity:" + key)
                                find_flag = False
                        if find_flag:
                            if value != constraint_value:
                                target = False
                                break
                    if target:
                        self.establish_link(entity, node_item, relationship_name)

        if node_item["label"] not in self.node_dict.keys():
            self.node_dict[node_item["label"]] = []
        self.node_dict[node_item["label"]].append(node_item)
        return node_item

    @staticmethod
    def transform_env(value, env_dict):
        if "$$" in str(value):
            temp_list = str(value).split("$$")
            i = 1
            while i < len(temp_list) - 1:
                temp_list[i] = env_dict[temp_list[i]]
                i += 2
            value = ''.join(temp_list)
        return value

    def establish_link(self, t_item, s_item, relationship):
        link = dict()
        link["stime"] = max(t_item["stime"], t_item["stime"])
        link["etime"] = 1645539492
        link["name"] = relationship
        link["label"] = relationship
        link["tid"] = t_item["id"]
        link["sid"] = s_item["id"]
        self.link_list.append(link.copy())
