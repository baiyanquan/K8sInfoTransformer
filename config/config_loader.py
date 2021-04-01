import os
import configparser
from kubernetes import config
from kubernetes.client import configuration


class ConfigLoader:
    def __init__(self):
        pass

    @staticmethod
    def load_k8s_config():
        current_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(current_path, 'k8s_config')
        config.kube_config.load_kube_config(config_file=config_path)

    @staticmethod
    def load_resource_config():
        # Initialize the config parser
        current_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(current_path, 'k8s_resource.ini')

        parser = configparser.ConfigParser()
        parser.read(config_path, encoding="utf-8")

        # Get all sections of the config file
        sections = parser.sections()

        # Initialize the return dict
        resource_config = {}

        # Traverse the sections and options
        for section in sections:

            resource_config[section] = {}
            options = parser.options(section)

            for option in options:
                # There are quotes in the resulting string so slice is used to remove them
                cur = parser.get(section, option)[1:-1]
                resource_config[section][option] = cur.split(",")

        return resource_config
