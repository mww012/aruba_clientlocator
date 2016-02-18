import paramiko
import time

class controller:
    def __init__(self, ip, user, pw, en):
        self.ip = ip
        self.user = user
        self.pw = pw
        self.en = en


    def connect(self):
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(self.ip, 22, self.user, self.pw)
        return conn

    def send_cmd(self, cmd):
        print cmd
        self.sh.send(cmd)
        time.sleep(2)
        print self.sh.recv(1024)