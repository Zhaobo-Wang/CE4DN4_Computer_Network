#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import time

from EchoClientServer import Client

########################################################################
# Echo-服务器类
########################################################################

########################################################################
# 一个基本的回声服务器，演示如何在套接字的接受(accept)和接收(recv)上设置超时。
# 请参阅下面的注释语句。在这里使用非阻塞套接字更好，但这只是对套接字超时的演示。
########################################################################

class Server:

    HOSTNAME = "0.0.0.0"
    PORT = 50000

    RECV_SIZE = 1024
    BACKLOG = 10
    
    MSG_ENCODING = "utf-8"

    ACCEPT_TIMEOUT = 1
    RECV_TIMEOUT = 1

    def __init__(self):
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # 创建一个IPv4 TCP套接字。
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # 获取套接字层的套接字选项。
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 将套接字绑定到套接字地址，即IP地址和端口。
            self.socket.bind((Server.HOSTNAME, Server.PORT))

            # 将套接字设置为监听状态。
            self.socket.listen(Server.BACKLOG)
            print("正在端口 {} 上监听...".format(Server.PORT))

            ############################################################
            # 设置监听套接字的超时时间。
            self.socket.settimeout(Server.ACCEPT_TIMEOUT)
            ############################################################

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # 接受一个回声客户端连接。当一个连接被接受时，
                # 将新的套接字引用传递给连接处理器。

                ########################################################
                # 使用try/except块捕获接受超时。
                # while True块将再次尝试接受。
                ########################################################
                try:
                    client = self.socket.accept()
                    self.connection_handler(client)
                except socket.timeout:
                    print("套接字接受超时...")
                ########################################################
                # try/except块结束
                ########################################################

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("从 {} 收到连接。".format(address_port))

        ################################################################
        # 为新套接字设置接收超时。
        connection.settimeout(Server.RECV_TIMEOUT);
        ################################################################

        while True:
            ########################################################
            # 开始try/except块以捕获接收超时。
            # while True块将再次尝试接收。
            ########################################################
            try:
                recvd_bytes = connection.recv(Server.RECV_SIZE)
            
                # 如果recv返回零字节，则TCP连接的另一端已关闭
                # （另一端可能在FIN WAIT 2状态，而我们在CLOSE WAIT状态）。如果是这样，
                # 关闭服务器端的连接并获取下一个客户端连接。
                if len(recvd_bytes) == 0:
                    print("关闭客户端连接... ")
                    connection.close()
                    break
                    
                # 将接收到的字节解码回字符串。然后输出它们。
                recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
                print("接收到: ", recvd_str)
                    
                # 将接收到的字节发送回客户端。
                connection.sendall(recvd_bytes)
                print("发送: ", recvd_str)
            except socket.timeout:
                    print("套接字接收超时...")
                    pass
            ############################################################
            # try/except块结束
            ############################################################

            except KeyboardInterrupt:
                print()
                print("关闭客户端连接... ")
                connection.close()
                break

########################################################################
# 如果直接运行，则处理命令行参数。
########################################################################

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################
