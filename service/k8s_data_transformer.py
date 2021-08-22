from dao.parse_template_loader import ParseTemplateLoader
from dao.k8s_data_loader import K8sDataLoader
from dao.json_result_writer import JsonResultWriter
from utils.utils import Utils
from collections import OrderedDict
from service.k8s_data_template_matching import K8sDataTemplateMatching
from service.k8s_data_filter import K8sDataFilter
from service.k8s_data_expansion import K8sDataExpansion
from datetime import datetime


class K8sDataTransformer:
    def __init__(self):
        # 解析模板准备
        self.parse_template = ParseTemplateLoader.load_parse_template()
        self.env_dict = ParseTemplateLoader.load_global_env()

        self.node_dict = OrderedDict()
        self.link_list = []
        self.arg_dict = dict()
        pass

    def transform_k8s_data(self, time):
        # 传递过来的时间可能不是简化版本的时间，一律进行过滤处理，然后获取对应时刻k8s的原始信息
        simplified_time = str(time).replace(" ", "_").replace("-", "").replace(":", "")
        k8s_data = K8sDataLoader.load_k8s_data(simplified_time)

        etime_str = simplified_time.replace("_", " ")
        etime_str = etime_str[0:4] + '-' + etime_str[4:6] + '-' + etime_str[6:8] + " " + etime_str[9:11] + ":" + etime_str[11:13] + ":" + etime_str[13:15]
        etime = Utils.datetime_timestamp(etime_str)

        # 构建出全部k8s信息的实体、关系dict
        result_dict = K8sDataTemplateMatching.template_matching(k8s_data, self.parse_template, self.env_dict, etime)

        # # 根据场景筛选出关键的实体、关系，场景为sdre_reset和sdr_p2p_network_loss，改变scenario的值即可切换，然后进行数据增强
        # scenario = "sdre_reset"
        # if scenario == "sdre_reset":
        #     result_dict = K8sDataFilter.sdr_reset_filter(result_dict)
        #     result_dict = K8sDataExpansion.add_sdre_component(result_dict)
        # elif scenario == "sdr_p2p_network_loss":
        #     result_dict = K8sDataFilter.sdr_p2p_network_loss_filter(result_dict)
        #     result_dict = K8sDataExpansion.mock_vusn_service(result_dict)
        #     result_dict = K8sDataExpansion.add_sdre_component(result_dict)
        #     result_dict = K8sDataExpansion.add_business_component(result_dict)

        json_result = dict()
        json_result["nodes"] = []
        for key, value in result_dict["nodes"].items():
            json_result["nodes"].extend(value)
        json_result["links"] = []
        for key, value in result_dict["links"].items():
            json_result["links"].extend(value)

        JsonResultWriter.write_json_data(simplified_time, json_result)

        return json_result


k8s_data_transformer = K8sDataTransformer()
k8s_data_transformer.transform_k8s_data("20210215_155600")
