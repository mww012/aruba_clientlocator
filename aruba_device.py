import paramiko
import time


class controller:
    def __init__(self, ip, user, pw, en):
        self.ip = ip
        self.user = user
        self.pw = pw
        self.en = en
        self.ssh = self.connect()
        self.aps = set()

    def connect(self):
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(self.ip, 22, self.user, self.pw)
        return conn

    def send_cmd(self, cmd):
        output = ''
        shell = self.ssh.invoke_shell()
        shell.send('en\n'+self.en+'\n'+'no paging\n')
        time.sleep(0.5)
        while shell.recv_ready():
            shell.recv(1024)
        for c in cmd:
            shell.send(c+'\n')
            time.sleep(.5)
            while shell.recv_ready():
                output += shell.recv(4096)
                time.sleep(.5)
        return output