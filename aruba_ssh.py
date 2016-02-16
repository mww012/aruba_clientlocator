import paramiko
import time
import re
import multiprocessing


def enum_controllers(master, user, pw, enpw):
    output = ''
    conn = connect_ssh(master, user, pw)
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
    conn.close()
    return controllers

def connect_ssh(ip, user, pw):
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(ip, 22, user, pw)
    return conn


def ssh_session(ip, user, pw, enpw, q):
    result = q.get()
    name = multiprocessing.current_process().name
    conn = connect_ssh(ip, user, pw)
    sh = conn.invoke_shell()
    time.sleep(0.5)

    # enable prompt
    sh.send('en\n')
    time.sleep(0.5)
    sh.send(enpw)
    sh.send('\n')
    time.sleep(0.5)

    while sh.recv_ready():
        sh.recv(1024)

    while result != 'close':
        print result, "command sent by", name
        sh.send(result)
        time.sleep(0.5)
        while sh.recv_ready():
            print sh.recv(1024)
        result = q.get()
        time.sleep(2)

    print "Caught close ", name
    conn.close()
