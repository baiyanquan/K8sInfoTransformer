from service.k8s_data_transformer import K8sDataTransformer


simplified_time_list = ["20210420_161200"]
for simplified_time in simplified_time_list:
    k8s_data_transformer = K8sDataTransformer()
    k8s_data_transformer.transform_k8s_data(simplified_time)
