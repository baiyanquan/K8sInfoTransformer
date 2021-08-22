import os
import configparser
from collections import OrderedDict
from kubernetes import config
from kubernetes.client import configuration


class ConfigLoader:
    def __init__(self):
        # Initialize the config parser
        current_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(current_path, 'k8s_resource.ini')
        self.parser = configparser.ConfigParser()
        self.parser.read(config_path, encoding="utf-8")

        # 暂时搁置的代码
        # current_path = os.path.dirname(os.path.realpath(__file__))
        # config_path = os.path.join(current_path, 'k8s_config')
        # config.kube_config.load_kube_config(config_file=config_path)

    def get_resource_file(self):
        resource_file_dict = OrderedDict()

        namespace = self.get_namespace()

        # Get all sections of the config file
        sections = self.parser.sections()

        # get global info
        if "global_info" in sections:
            options = self.parser.options("global_info")
            for option in options:
                resource_file_dict[option] = self.parser.get("global_info", option)[1:-1]
        else:
            print("Invalid key \"global_info\"")

        # get local info
        if "local_info" in sections:
            options = self.parser.options("local_info")
            for option in options:
                resource_file_dict[option] = namespace + "__" + self.parser.get("local_info", option)[1:-1]
        else:
            print("Invalid key \"local_info\"")
        return resource_file_dict

    def get_template_file(self):
        template_file_dict = dict()

        # Get all sections of the config file
        sections = self.parser.sections()

        # get info cmd
        if "template" in sections:
            options = self.parser.options("template")
            for option in options:
                template_file_dict[option] = self.parser.get("template", option)[1:-1]
        else:
            print("Invalid key \"template\"")
        return template_file_dict

    def get_generation_cmd(self):
        cmd_dict = dict()

        general = ""
        output_format = ""

        # Get all sections of the config file
        sections = self.parser.sections()

        # get info cmd
        if "get_info_cmd" in sections:
            options = self.parser.options("get_info_cmd")
            if "general" in options:
                general = self.parser.get("get_info_cmd", "general")[1:-1]
            else:
                print("Invalid key \"general\"")
            if "output_format" in options:
                output_format = self.parser.get("get_info_cmd", "output_format")[1:-1]
            else:
                print("Invalid key \"general\"")
        else:
            print("Invalid key \"get_info_cmd\"")

        namespace = self.get_namespace()
        resource_dict = self.get_resource()
        for global_resource in resource_dict["global"]:
            cmd_dict[global_resource] = general + global_resource + output_format
        for local_resource in resource_dict["local"]:
            cmd_dict[local_resource] = general + local_resource + " -n " + namespace + output_format

        return cmd_dict

    def get_resource(self):
        resource_dict = {
            "global": [],
            "local": []
        }

        # Get all sections of the config file
        sections = self.parser.sections()

        # get global resource
        if "global_resource" in sections:
            options = self.parser.options("global_resource")
            if "resource_type" in options:
                resource_dict["global"] = self.parser.get("global_resource", "resource_type")[1:-1].split(",")
            else:
                print("Invalid key \"resource_type\"")
        else:
            print("Invalid key \"global_resource\"")

        # get local resource
        if "local_resource" in sections:
            options = self.parser.options("local_resource")
            if "resource_type" in options:
                resource_dict["local"] = self.parser.get("local_resource", "resource_type")[1:-1].split(",")
            else:
                print("Invalid key \"resource_type\"")
        else:
            print("Invalid key \"local_resource\"")
        return resource_dict

    def get_namespace(self):
        namespace = ""

        # Get all sections of the config file
        sections = self.parser.sections()

        # get namespace
        if "global" in sections:
            options = self.parser.options("global")
            if "namespace" in options:
                namespace = self.parser.get("global", "namespace")[1:-1]
            else:
                print("Invalid key \"namespace\"")
        else:
            print("Invalid key \"global\"")

        return namespace
