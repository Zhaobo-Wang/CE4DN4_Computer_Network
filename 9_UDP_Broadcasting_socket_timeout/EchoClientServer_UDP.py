#!/usr/bin/env python3

# 导入必要的库
import socket
import argparse
import sys
import time

# Echo服务器类定义
class Server:

    # 服务器主机名和端口号设置
    HOSTNAME = "0.0.0.0"  # 使用socket.gethostname()可获取当前主机名
    PORT = 50000  # 设置监听端口为50000

    # 接收数据的大小设置
    RECV_SIZE = 256
    # 设置消息编码方式
    MSG_ENCODING = "utf-8"

    # 类的初始化函数
    def __init__(self):
        self.create_listen_socket()  # 创建和配置套接字
        self.process_messages_forever()  # 开始处理消息

    # 创建和绑定监听套接字的函数
    def create_listen_socket(self):
        try:
            # 创建一个IPv4 UDP套接字
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 设置套接字选项
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 将套接字绑定到地址和端口
            self.socket.bind((Server.HOSTNAME, Server.PORT))
            print("正在监听端口 {} ...".format(Server.PORT))

        except Exception as msg:
            print(msg)
            sys.exit(1)

    # 持续处理消息的函数
    def process_messages_forever(self):
        try:
            while True:
                # 使用recvfrom接收消息，以获取发送者身份
                self.message_handler(self.socket.recvfrom(Server.RECV_SIZE))

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            print("关闭服务器套接字 ...")
            self.socket.close()
            sys.exit(1)

    # 处理接收到的消息的函数
    def message_handler(self, client):
        # recvfrom返回接收到的数据内容和发送者身份
        msg_bytes, address_port = client
        msg = msg_bytes.decode(Server.MSG_ENCODING)
        print("-" * 72)
        print("{} 发来的消息.".format(address_port))
        # 将接收到的消息回显给发送者
        self.socket.sendto(msg_bytes, address_port)
        print("回显的消息: ", msg)


# Echo客户端类定义
class Client:

    # 服务器地址和端口设置
    SERVER_ADDRESS_PORT = ('localhost', Server.PORT)
    # 接收数据的大小设置
    RECV_SIZE = 256

    # 类的初始化函数
    def __init__(self):
        self.get_socket()  # 获取套接字
        self.send_console_input_forever()  # 开始发送消息

    # 获取套接字的函数
    def get_socket(self):
        try:
            # 创建一个IPv4 UDP套接字
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 设置套接字选项
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        except Exception as msg:
            print(msg)
            sys.exit(1)

    # 获取控制台输入的函数
    def get_console_input(self):
        # 循环直到用户输入非空行
        while True:
            self.input_text = input("输入: ")
            if self.input_text != '':
                self.input_text_encoded = self.input_text.encode(Server.MSG_ENCODING)
                break

    # 持续发送控制台输入的函数
    def send_console_input_forever(self):
        while True:
            try:
                self.get_console_input()
                self.message_send()
                self.message_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("关闭客户端套接字 ...")
                self.socket.close()
                sys.exit(1)

    # 发送消息的函数
    def message_send(self):
        try:
            # sendto用于发送消息并指明目的地
            self.socket.sendto(self.input_text_encoded, Client.SERVER_ADDRESS_PORT)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    # 接收消息的函数
    def message_receive(self):
        try:
            # recvfrom用于接收消息和发送者身份
            recvd_bytes, address = self.socket.recvfrom(Client.RECV_SIZE)
            print("收到的消息: ", recvd_bytes.decode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)


########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

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