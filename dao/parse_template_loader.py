import yaml
import os
from config.config_loader import ConfigLoader


class ParseTemplateLoader:
    def __init__(self):
        pass

    @staticmethod
    def load_global_env():
        template_base_path = ParseTemplateLoader.get_base_path()
        template_path = os.path.join(template_base_path, "global_env.yaml")
        return ParseTemplateLoader.parse_template(template_path)

    @staticmethod
    def load_parse_template():
        template_base_path = ParseTemplateLoader.get_base_path()

        result = {}

        config_loader = ConfigLoader()
        template_file_list = config_loader.get_template_file()

        for resource_type, template_file in template_file_list.items():
            template_path = os.path.join(template_base_path, template_file)
            if os.path.exists(template_path):
                result[resource_type] = ParseTemplateLoader.parse_template(template_path)
            else:
                print("Invalid path " + str(template_path))
                continue

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
        template_base_path = os.path.join(template_base_path, 'k8s')
        if not os.path.exists(template_base_path):
            print("Invalid template url: " + template_base_path)
            return ""
        return template_base_path


ParseTemplateLoader.load_parse_template()