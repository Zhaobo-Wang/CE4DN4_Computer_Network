#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import time
import struct
import ipaddress

########################################################################
# Multicast Address and Port
########################################################################

# MULTICAST_ADDRESS = "239.1.1.1"
MULTICAST_ADDRESS = "239.2.2.2"

MULTICAST_PORT = 2000

# Make them into a tuple.
MULTICAST_ADDRESS_PORT = (MULTICAST_ADDRESS, MULTICAST_PORT)

# Ethernet/Wi-Fi interface address
IFACE_ADDRESS = "192.168.1.22"

########################################################################
# 多播地址和端口
########################################################################

# MULTICAST_ADDRESS = "239.1.1.1"
MULTICAST_ADDRESS = "239.2.2.2"  # 设置多播地址

MULTICAST_PORT = 2000  # 设置多播端口

# 将它们组合成一个元组
MULTICAST_ADDRESS_PORT = (MULTICAST_ADDRESS, MULTICAST_PORT)

# 以太网/无线接口地址
IFACE_ADDRESS = "192.168.1.22"

########################################################################
# 多播发送者
########################################################################

class Sender:

    HOSTNAME = socket.gethostname()  # 获取本地主机名

    TIMEOUT = 2  # 超时时间
    RECV_SIZE = 256  # 接收大小
    
    MSG_ENCODING = "utf-8"  # 消息编码方式
    MESSAGE =  HOSTNAME + " multicast beacon: "  # 要发送的消息
    MESSAGE_ENCODED = MESSAGE.encode('utf-8')  # 对消息进行编码

    # 创建一个多播包中使用的最大跳数（TTL, Time-To-Live）的1字节
    TTL = 1 # 多播的跳数限制
    TTL_BYTE = TTL.to_bytes(1, byteorder='big')
    # 或者: TTL_BYTE = struct.pack('B', TTL)
    # 或者: TTL_BYTE = b'01'

    def __init__(self):
        self.create_send_socket()
        self.send_messages_forever()

    def create_send_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            ############################################################
            # 设置多播的TTL

            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, Sender.TTL_BYTE)

            ############################################################
            # 绑定到将携带多播数据包的接口，或者你可以让操作系统决定，对于笔记本电脑或简单的桌面系统通常是可行的。
            # 在绑定中包含端口，或者让操作系统选择。

            # self.socket.bind((IFACE_ADDRESS, 30000)) # 绑定到端口30000。
            self.socket.bind((IFACE_ADDRESS, 0)) # 让系统选择一个端口号。

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def send_messages_forever(self):
        try:
            beacon_sequence_number = 1
            while True:
                print("发送多播信标 {} {}".format(beacon_sequence_number, MULTICAST_ADDRESS_PORT))
                beacon_bytes = Sender.MESSAGE_ENCODED + str(beacon_sequence_number).encode('utf-8')

                ########################################################
                # 发送多播数据包
                self.socket.sendto(beacon_bytes, MULTICAST_ADDRESS_PORT)

                # 稍作休息，然后发送另一个。
                time.sleep(Sender.TIMEOUT)
                beacon_sequence_number += 1
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)

########################################################################
# 多播接收器
########################################################################
#
# 我们需要做两件事：
#
# 1. 向操作系统发出信号，表明我们想要加入一个多播组，以便
#    捕获到达指定接口的多播数据包。这也会确保多播路由器
#    将数据包转发给我们。注意，多播位于网络层，此时不涉及端口。
#
# 2. 绑定到适当的地址/端口（网络层/传输层），以便在该接口上
#    到达的数据包被正确过滤，我们能接收到指定地址和端口的数据包。
#
############################################
# 1. 加入多播组设置
############################################
#
# 向操作系统发出信号，表明您想加入特定的多播组地址
# 在指定的接口上。通过setsockopt函数调用实现。
# 多播地址和接口（地址）是添加组成员请求的一部分，
# 传递给底层。
#
# 这是通过上面定义的MULTICAST_ADDRESS和下面定义的
# RX_IFACE_ADDRESS完成的。
#
# 如果为接收接口选择"0.0.0.0"，系统将选择接口，
# 这通常能够正常工作。在更复杂的情况下，例如，您可能有多个网络
# 接口，您可能需要通过使用其地址显式指定接口，如下例所示。

# RX_IFACE_ADDRESS = "0.0.0.0"
# RX_IFACE_ADDRESS = "127.0.0.1"
RX_IFACE_ADDRESS = IFACE_ADDRESS  # 使用先前定义的接口地址

#################################################
# 2. 多播接收器绑定（即过滤）设置
#################################################
#
# 接收器套接字绑定的地址。这在IP/UDP级别用于
# 过滤传入的多播接收。使用"0.0.0.0"通常能够正常工作。
# 使用单播地址进行绑定，例如 RX_BIND_ADDRESS =
# "192.168.1.22"，在Linux上失败，因为到达的数据包不带有这个
# 目的地址。
#

RX_BIND_ADDRESS = "0.0.0.0"
# RX_BIND_ADDRESS = MULTICAST_ADDRESS # 在Linux/MacOS上可以，但在Windows 10上不行。

# 接收器套接字将绑定到以下地址和端口。
RX_BIND_ADDRESS_PORT = (RX_BIND_ADDRESS, MULTICAST_PORT)

########################################################################

class Receiver:

    RECV_SIZE = 256  # 接收大小

    def __init__(self):
        print("绑定地址/端口 = ", RX_BIND_ADDRESS_PORT)
        
        self.get_socket()
        self.receive_forever()

    def get_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            # 对于MacOS，使用以下代替：
            # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)

            ############################################################            
            # 绑定到一个地址/端口。在多播中，这被视为一个"过滤器"，
            # 决定了哪些数据包能到达UDP应用。
            ############################################################            
            self.socket.bind(RX_BIND_ADDRESS_PORT)

            ############################################################
            # 多播请求必须包含一个由8个字节组成的字节对象。
            # 前4个字节是多播组地址。后4个字节是要使用的接口地址。
            # 所有网络接口的全零I/F地址。它们必须是网络字节顺序。
            ############################################################
            multicast_group_bytes = socket.inet_aton(MULTICAST_ADDRESS)
            # 或
            # multicast_group_int = int(ipaddress.IPv4Address(MULTICAST_ADDRESS))
            # multicast_group_bytes = multicast_group_int.to_bytes(4, byteorder='big')
            # 或
            # multicast_group_bytes = ipaddress.IPv4Address(MULTICAST_ADDRESS).packed
            print("多播组: ", MULTICAST_ADDRESS)

            # 设置要使用的接口。
            multicast_iface_bytes = socket.inet_aton(RX_IFACE_ADDRESS)

            # 形成多播请求。
            multicast_request = multicast_group_bytes + multicast_iface_bytes
            print("multicast_request = ", multicast_request)

            # 您可以使用struct.pack来创建请求，但这更复杂，例如，
            # 'struct.pack("<4sl", multicast_group_bytes,
            # int.from_bytes(multicast_iface_bytes, byteorder='little'))'
            # 或 'struct.pack("<4sl", multicast_group_bytes, socket.INADDR_ANY)'

            # 发出多播IP添加组成员请求。
            print("添加组成员（地址/接口）: ", MULTICAST_ADDRESS,"/", RX_IFACE_ADDRESS)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def receive_forever(self):
        while True:
            try:
                data, address_port = self.socket.recvfrom(Receiver.RECV_SIZE)
                address, port = address_port
                print("收到: {} {}".format(data.decode('utf-8'), address_port))
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











