#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import time

########################################################################
# Broadcast Server class
########################################################################

class Sender:

    HOSTNAME = socket.gethostname()  # 获取当前主机名

    # 定期发送广播数据包。设置周期（秒）。
    BROADCAST_PERIOD = 2

    # 定义要广播的消息。
    MSG_ENCODING = "utf-8"  # 消息编码格式
    MESSAGE =  "Hello from " + HOSTNAME  # 广播的消息
    MESSAGE_ENCODED = MESSAGE.encode('utf-8')  # 将消息编码为UTF-8格式

    # 使用广播地址或定向广播地址。定义一个广播端口。
    BROADCAST_ADDRESS = "255.255.255.255"  # 或者可以是定向广播地址
    # BROADCAST_ADDRESS = "192.168.1.255"
    BROADCAST_PORT = 30000
    ADDRESS_PORT = (BROADCAST_ADDRESS, BROADCAST_PORT)  # 组合地址和端口

    def __init__(self):
        self.create_sender_socket()  # 创建发送者套接字
        self.send_broadcasts_forever()  # 持续发送广播

    def create_sender_socket(self):
        try:
            # 设置一个UDP套接字。
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 设置套接字层的套接字选项。
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 设置广播的选项。
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # 在更复杂的情况下，您可能需要绑定到一个接口。
            # 这是为了确保广播通过正确的接口发送出去，例如：
            self.socket.bind(("", 33333))  # 绑定特定接口和端口
            # self.socket.bind(("127.0.0.1", 33333))         
                
        except Exception as msg:
            print(msg)
            sys.exit(1)  # 出现异常则退出程序

    def send_broadcasts_forever(self):
        try:
            while True:  # 无限循环发送广播
                print("Sending to {} ...".format(Sender.ADDRESS_PORT))  # 打印发送信息
                self.socket.sendto(Sender.MESSAGE_ENCODED, Sender.ADDRESS_PORT)  # 发送编码后的消息
                time.sleep(Sender.BROADCAST_PERIOD)  # 等待一定时间
        except Exception as msg:
            print(msg)  # 打印异常信息
        except KeyboardInterrupt:
            print()  # 捕获中断信号
        finally:
            self.socket.close()  
            sys.exit(1)  


########################################################################
# Echo Receiver class
########################################################################

class Receiver:

    RECV_SIZE = 256

    HOST = "0.0.0.0"
    # HOST = "192.168.1.255"
    # HOST = "255.255.255.255"
    ADDRESS_PORT = (HOST, Sender.BROADCAST_PORT)

    def __init__(self):
        self.get_socket()
        self.receive_forever()

    def get_socket(self):
        try:
            # Create an IPv4 UDP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Set socket layer socket options.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to all interfaces and the agreed on broadcast port.
            self.socket.bind(Receiver.ADDRESS_PORT)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def receive_forever(self):
        while True:
            try:
                data, address = self.socket.recvfrom(Receiver.RECV_SIZE)
                print("Broadcast received: ", 
                      data.decode('utf-8'), address)
            except KeyboardInterrupt:
                print(); exit()
            except Exception as msg:
                print(msg)
                sys.exit(1)

########################################################################
# Process command line arguments if run directly.
########################################################################

if __name__ == '__main__':
    roles = {'receiver': Receiver,'sender': Sender}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='sender or receiver role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################






