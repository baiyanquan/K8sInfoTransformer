from utils.utils import Utils
from service.k8s_observer import K8sObserver


class K8sDataPicker(object):
    def __init__(self):
        pass

    @staticmethod
    def get_k8s_resource_info():
        K8sObserver.get_info()
        return "a"




