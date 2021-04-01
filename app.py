import time
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from service.k8s_data_transformer import K8sDataTransformer
from service.k8s_observer import K8sObserver
import paramiko


def job(text):
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    simplified_time = str(t).replace("-", "").replace(" ", "_").replace(":", "")
    K8sObserver.get_k8s_info(simplified_time)
    k8s_data_transformer = K8sDataTransformer()
    k8s_data_transformer.transform_k8s_data(simplified_time)
    print('{} --- {}'.format(text, t))


s = paramiko.SSHClient()
s.load_system_host_keys()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect(hostname="192.168.199.31", port=int(22), username="root", password="tongji409")

scheduler = BlockingScheduler()
now_date = datetime.datetime.now()
start_date = (now_date+datetime.timedelta(seconds=15)).strftime('%Y-%m-%d %H:%M:%S')
end_date = (now_date+datetime.timedelta(minutes=20, seconds=15)).strftime('%Y-%m-%d %H:%M:%S')
scheduler.add_job(job, 'interval', seconds=15, start_date=start_date, end_date=end_date, args=['get_k8s_info'])

scheduler.start()
