#!/usr/bin/python3

"""
Echo Client and Server Classes

T. D. Todd
McMaster University

to create a Client: "python EchoClientServer.py -r client" 
to create a Server: "python EchoClientServer.py -r server" 

or you can import the module into another file, e.g., 
import EchoClientServer
e.g., then do EchoClientserver.Server()

"""

########################################################################

import socket
import argparse
import sys

########################################################################
# Echo Server class
########################################################################

class Server:

    # Set the server hostname used to define the server socket address
    # binding. Note that "0.0.0.0" or "" serves as INADDR_ANY. i.e.,
    # bind to all local network interfaces.
    # HOSTNAME = "192.168.1.22" # single interface    
    # HOSTNAME = "hornet"       # valid hostname (mapped to address/IF)
    # HOSTNAME = "localhost"    # local host (mapped to local address/IF)
    HOSTNAME = "127.0.0.1"    # same as localhost
    # HOSTNAME = "0.0.0.0"      # All interfaces.
    
    # 服务器的主机名和端口号。这里设置了几个选项，如 "127.0.0.1" 表示只接受来自本机的连接。
    PORT = 50000
    
    RECV_BUFFER_SIZE = 1024 # 定义了接收数据的缓冲区大小
    MAX_CONNECTION_BACKLOG = 10 # 设置了服务器可以接受的最大未处理连接数



    # 定义了消息的编码格式，这里可以是 ASCII 或 UTF-8
    # MSG_ENCODING = "ascii" 
    MSG_ENCODING = "utf-8"

    # 是一个元组，包含主机名和端口号，用于创建套接字地址
    SOCKET_ADDRESS = (HOSTNAME, PORT)

    def __init__(self):
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            '''
            创建一个 IPv4 TCP socket。
            设置socket选项 允许重新使用地址。
            绑定socket到指定的地址和端口。
            设置socket为监听状态 等待客户端连接。
            '''
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(Server.SOCKET_ADDRESS)
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))


        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                '''
                创建了一个无限循环。这是常见的模式，用于持续监听和处理进入的客户端连接。
                由于这是一个永不终止的循环，它将一直运行，直到被外部条件（如异常）打断。
                '''
                self.connection_handler(self.socket.accept())
                '''
                调用等待并接受一个进入的连接。accept()方法在一个新客户端连接到服务器时返回两个值：
                一个新的socket对象和客户端的地址。这个新的socket用于与客户端通信
                '''
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
            '''
            这通常是因为用户按下了中断键(如 Ctrl+C)。这样做可以优雅地停止服务器。
            '''
        finally:
            '''
            这里它关闭socket并退出程序。关闭套接字是释放系统资源的重要步骤,
            确保没有悬挂的socket连接。
            sys.exit(1) 退出程序 返回状态1通常表示异常终止。
            '''
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        
        '''
        函数接收一个名为 client 的参数，
        这个参数是一个包含了连接和地址端口的元组 (connection, address_port)
        '''
        connection, address_port = client

        '''打印出 client 参数，显示完整的客户端连接信息。'''

        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        print(client)

        while True:
            try:
                '''
                使用 connection.recv(Server.RECV_BUFFER_SIZE) 从连接中接收数据。
                这里 Server.RECV_BUFFER_SIZE 定义了接收缓冲区的大小
                '''
                recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE)
            
                '''
                如果 recv 返回的字节数为 0, 说明客户端关闭了 TCP 连接。
                这时，服务器端也关闭连接并退出循环，等待下一个客户端连接。
                '''
                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")
                    connection.close()
                    break

                '''
                接收到的字节数据通过 decode(Server.MSG_ENCODING) 转换成字符串，
                这里的 Server.MSG_ENCODING 定义了字符编码格式
                '''
                recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
                print("Received: ", recvd_str)
                
                '''
                将接收到的原始字节数据发送回客户端。
                '''
                connection.sendall(recvd_bytes)
                print("Sent: ", recvd_str)

            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break

########################################################################
# Echo Client class
########################################################################

class Client:

    # Set the server to connect to. If the server and client are running
    # on the same machine, we can use the current hostname.
    # SERVER_HOSTNAME = socket.gethostname()
    # SERVER_HOSTNAME = "192.168.1.22"
    SERVER_HOSTNAME = "localhost"
    
    # Try connecting to the compeng4dn4 echo server. You need to change
    # the destination port to 50007 in the connect function below.
    #SERVER_HOSTNAME = 'compeng4dn4.mooo.com'

    RECV_BUFFER_SIZE = 1024 # Used for recv.    
    # RECV_BUFFER_SIZE = 5 # Used for recv.    


    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()

    def get_socket(self):
        try:
            '''
            创建一个新的socket, 用于网络通信。
            设置socket选项, 允许在同一端口上快速重新绑定。
            如果出现异常(如无法创建socket),则打印错误消息并退出程序。
            '''
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            '''
            如果连接成功，打印连接信息；如果失败，打印错误信息并退出程序。
            '''
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
            print("Connected to \"{}\" on port {}".format(Client.SERVER_HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        '''
        从控制台获取用户输入，如果输入非空，则跳出循环
        '''
        while True:
            self.input_text = input("Input: ")
            if self.input_text != "":
                break
    
    def send_console_input_forever(self):
        while True:
            try:
                self.get_console_input()
                self.connection_send()
                self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                # If we get and error or keyboard interrupt, make sure
                # that we close the socket.
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:
            '''
            将用户输入的文本编码成字节后发送到服务器
            '''
            self.socket.sendall(self.input_text.encode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            '''
            接收服务器的响应数据，解码后打印到控制台。
            如果接收到的数据长度为零(即服务器关闭连接),则关闭socket并退出程序
            '''
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))

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






