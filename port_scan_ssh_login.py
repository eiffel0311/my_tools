import IPy
import Queue
import nmap
import pexpect
import threading

screenLock = threading.Semaphore(value = 1)
ip_all_queue = Queue.Queue()


def analysis_ips(ip_range):
    ips = IPy.IP(ip_range)
    return ips

def scan_active_ip(ip):
    nm_scan = nmap.PortScanner()
    nm_scan.scan(ip, '22')
    state = nm_scan[ip]['tcp'][22]['state']
    return state

def verify_password(ip, password):
    try:
        ssh_newkey = "Are you sure you want to continue connecting (yes/no)?"
        connStr = 'ssh root@' + ip
        child = pexpect.spawn(connStr)
        ret = child.expect([pexpect.TIMEOUT, ssh_newkey, "root@" + ip + "'s password:", '#', '>>>', '>', '\$'])
        if ret >= 3 and ret <= 6:
            return True
        if ret == 0:
            return False
        if ret == 1:
            child.sendline("yes")
            ret = child.expect([pexpect.TIMEOUT, ssh_newkey, "root@" + ip + "'s password:", '#', '>>>', '>', '\$'])
        if ret == 0:
            return False
    
        child.sendline(password)
        ret = child.expect([pexpect.TIMEOUT, ssh_newkey, "root@" + ip + "'s password:", '#', '>>>', '>', '\$'])
        if ret >= 3 and ret <= 6:
            return True
        return False
    except Exception, e:
        #print str(e)
        return False
        

def main(ip, password):
    if verify_password(ip, password):
        screenLock.acquire()
        print ip, " is password : " , password
        screenLock.release()

for ip in analysis_ips('192.168.0.0/16'):
    if scan_active_ip(str(ip)) == 'open':
        print ip , '22 opend!!!'
        ip_all_queue.put({'ip': ip, 'password': 'www.zx.c0m'})

for i in range(10):
    while not ip_all_queue.empty():
        ip_password = ip_all_queue.get()
        ip = ip_password['ip']
        password = ip_password['password']
        t = threading.Thread(target = main, args = (str(ip), password,))
        t.start()