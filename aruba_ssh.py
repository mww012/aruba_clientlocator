import paramiko
import time
import re


def enum_controllers(master, user, pw, enpw):
    output = ''
    conn = connect_ssh(master, user, pw)
    print "enum_controllers"
    sh = conn.invoke_shell()
    time.sleep(0.5)

    # enable prompt
    sh.send('en\n')
    time.sleep(0.5)
    sh.send(enpw)
    sh.send('\n')
    time.sleep(0.5)

    # get local switches
    while sh.recv_ready():
        sh.recv(1024)
    sh.send('show switches\n')
    time.sleep(0.5)
    output += sh.recv(1024)
    controllers = re.findall(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)", output)
    return controllers


def connect_ssh(ip, user, pw):
    print "connect_ssh"
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(ip, 22, user, pw)
    return conn


def ssh_session(ip, user, pw):
    print ip, user

