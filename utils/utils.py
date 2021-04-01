import time
import datetime
# import paramiko


class Utils:
    @staticmethod
    def datetime_timestamp(dt):
        time.strptime(dt, '%Y-%m-%d %H:%M:%S')
        s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
        return int(s)

    @staticmethod
    def timestamp_datetime(ts):
        dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return dt

    @staticmethod
    def get_now_datetime():
        now_time = time.localtime(time.time())
        result = {"standard_format": time.strftime('%Y-%m-%d %H:%M:%S', now_time),
                  "simplified_format": time.strftime('%Y%m%d_%H%M%S', now_time),
                  "timestamp": Utils.datetime_timestamp(time.strftime('%Y-%m-%d %H:%M:%S', now_time))}
        return result

    # @staticmethod
    # def verification_ssh(host, username, password, port, root_pwd, cmd):
    #     s = paramiko.SSHClient()
    #     s.load_system_host_keys()
    #     s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     s.connect(hostname=host, port=int(port), username=username, password=password)
    #     if username != 'root':
    #         ssh = s.invoke_shell()
    #         time.sleep(0.1)
    #         ssh.send('su root \n')
    #         buff = ''
    #         while not buff.endswith('Password: '):
    #             resp = ssh.recv(9999)
    #             buff += resp.decode("utf-8")
    #         ssh.send(root_pwd)
    #         ssh.send('\n')
    #         buff = ''
    #         while not buff.endswith('# '):
    #             resp = ssh.recv(9999)
    #             buff += resp.decode("utf-8")
    #         ssh.send(cmd)
    #         ssh.send('\n')
    #         buff = ''
    #         while not buff.endswith('# '):
    #             resp = ssh.recv(9999)
    #             buff += resp.decode("utf-8")
    #         s.close()
    #         result = buff
    #     else:
    #         stdin, stdout, stderr = s.exec_command(cmd)
    #         result = stdout.read()
    #         s.close()
    #     return result
