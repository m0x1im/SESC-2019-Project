import socket
import time

ipcommand = "HIS(" + socket.gethostbyname(socket.gethostname()) + ")"
ipcommand = ipcommand.encode("utf-8")

def broadcastInit(port):
    global server

    ### Server init ###
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(("", port))
    server.settimeout(60)
    print(socket.gethostbyname(socket.gethostname()))

def broadcastIpAnnounsing(interval, port):
    ### This code will send a server IP every [interval] seconds ###
    global server
    while True:
        server.sendto(ipcommand, ('255.255.255.255', port))
        time.sleep(interval)

def broadcastListener(port):
    ### This code will waiting for a IP request ###
    global server
    while True:
        try:
            data, addr = server.recvfrom(1024)
            if data == b"HIS(init)":
                broadcastSendIP(port)
            print("Тут что-то пришло, чекай: \"%s\""%data)
            print("От него: ", addr)
        except socket.timeout:
            print("timeout")
            print("continue working")

def broadcastSendIP(port):
    server.sendto(ipcommand, ('255.255.255.255', port))