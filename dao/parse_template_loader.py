import yaml
import os
from config.config_loader import ConfigLoader


class ParseTemplateLoader:
    def __init__(self):
        pass

    @staticmethod
    def load_parse_template():
        template_base_path = ParseTemplateLoader.get_base_path()

        result = {}

        if not os.path.exists(template_base_path):
            print("Wrong template url!")
            return result

        template_list = []
        resource_type_list = ConfigLoader.load_resource_config()
        template_list.extend(resource_type_list["global_resource"]["resource_type"])
        template_list.extend(resource_type_list["local_resource"]["resource_type"])

        for template in template_list:
            template_path = os.path.join(template_base_path, template + ".yaml")
            if not os.path.exists(template_path):
                print("Invalid path!")
                continue
            elif os.path.isdir(template_path):
                print("Cannot parse directory in k8s templates!")
                continue
            else:
                result[template.replace(".yaml", "")] = ParseTemplateLoader.parse_template(template_path)

        return result

    @staticmethod
    def parse_template(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.load(f.read(), Loader=yaml.FullLoader)
        return template

    @staticmethod
    def get_resource_type_list():
        result = []
        for template in os.listdir(ParseTemplateLoader.get_base_path()):
            result.append(template.replace(".yaml", ""))
        return result

    @staticmethod
    def get_base_path():
        current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        template_base_path = os.path.join(current_path, 'template')
        return os.path.join(template_base_path, 'k8s')
