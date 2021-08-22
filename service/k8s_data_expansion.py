from collections import OrderedDict

"""
数据扩充：补足k8s data中缺失的相关信息
"""


class K8sDataExpansion:
    def __init__(self):
        pass

    @staticmethod
    def mock_vusn_service():
        mock_data = {
            "id": "4716007-3c13-3cze-adzb-810a45b46520",
            "name": "http://uvc05/service/vusn-pod",
            "stime": "",
            "etime": "",
            "label": "Service",
            "namespace": "uvc05",
            "property": {
                "query": {

                },
                "query_range": {

                }
            }
        }
        return mock_data



