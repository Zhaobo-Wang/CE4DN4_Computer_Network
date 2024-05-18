
'''
# Simple File Request/Download Protocol


当客户端连接到服务器并想要请求下载文件时，
它会发送以下消息: 1字节的GET命令 + 1字节的文件名大小字段 + 请求的文件名，例如，


# ------------------------------------------------------------------
# | 1 byte GET command  | 1 byte filename size | ... file name ... |
# ------------------------------------------------------------------

服务器检查GET命令,然后传输请求的文件。
服务器传输的文件数据前会加上一个8字节的文件大小字段,如下所示:

# -----------------------------------
# | 8 byte file size | ... file ... |
# -----------------------------------

服务器需要定义一个名为REMOTE_FILE_NAME的文本文件,客户端可以请求此文件。
客户端将使用文件名LOCAL_FILE_NAME存储下载的文件。
这样您就可以在同一个目录下运行服务器和客户端,而不会覆盖文件。

'''


import socket
import argparse
import time

########################################################################

# 定义所有数据包协议字段长度。

CMD_FIELD_LEN            = 1 # 从客户端发送的1字节命令。
FILENAME_SIZE_FIELD_LEN  = 1 # 1字节文件名大小字段。
FILESIZE_FIELD_LEN       = 8 # 8字节文件大小字段。
    
# 定义命令的字典。实际的命令字段值必须是1字节整数。目前，我们只定义了“GET”命令，
# 该命令告诉服务器发送一个文件。

CMD = {"GET" : 2}

MSG_ENCODING = "utf-8"
SOCKET_TIMEOUT = 4

########################################################################
# recv_bytes函数是recv的前端
########################################################################

'''

调用recv从套接字读取bytecount_target字节。返回一个状态 (True 或 False)
和接收到的字节（前者情况下）。

'''

def recv_bytes(sock, bytecount_target):
    
    '''
    如果我们被给了错误的信息，请确保套接字超时。
    '''
    sock.settimeout(SOCKET_TIMEOUT)

    '''
    这个函数的作用是从网络连接中安全、准确地接收指定数量的字节，
    这是网络通信中常见的需求，特别是在接收固定大小的消息或文件时。
    '''
    
    try:
        byte_recv_count = 0 
        recv_bytes = b''
        '''
        这里设置了两个变量: 
            byte_recv_count 用于追踪已经接收的字节数，
            而 recv_bytes 用于储存接收到的字节序列。
        '''
        while byte_recv_count < bytecount_target:
            new_bytes = sock.recv(bytecount_target-byte_recv_count)
            '''
            这行代码从套接字请求数据。sock.recv() 方法尝试接收指定数量的字节，
            这个数量是目标字节数减去已经接收的字节数。这样可以确保不会尝试接收超过所需的数据。
            '''

            if not new_bytes:
                return(False, b'')
            
            byte_recv_count += len(new_bytes)
            recv_bytes += new_bytes
            
            '''
            如果接收到了数据，将新接收的字节长度添加到 byte_recv_count,
            并将接收到的字节追加到 recv_bytes。
            '''

        # 如果我们正确完成，关闭套接字超时。
        sock.settimeout(None)            
        return (True, recv_bytes)
    
    # 如果套接字超时，说明出现了问题。返回一个False状态。
    except socket.timeout:
        sock.settimeout(None)        
        print("recv_bytes: 接收套接字超时!")
        return (False, b'')



########################################################################
# SERVER
########################################################################

class Server:

    HOSTNAME = "127.0.0.1"

    PORT = 50000
    RECV_SIZE = 1024
    BACKLOG = 5

    FILE_NOT_FOUND_MSG = "Error: Requested file is not available!"

    # REMOTE_FILE_NAME = "greek.txt"
    # REMOTE_FILE_NAME = "twochars.txt"
    REMOTE_FILE_NAME = "D:/McMaster/4DN4/lab3/server_send/ocanada_greek.txt"
    # REMOTE_FILE_NAME = "ocanada_english.txt"

    def __init__(self):
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # Create the TCP server listen socket in the usual way.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((Server.HOSTNAME, Server.PORT))
            self.socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            exit()

    def process_connections_forever(self):
        try:
            while True:
                self.connection_handler(self.socket.accept())
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()

    def connection_handler(self, client):

        connection, address = client
        print("-" * 72)
        print("Connection received from {}.".format(address))

        ################################################################
        # 处理连接并查看客户端是否请求了我们持有的文件。
        
        # 读取命令并检查是否为GET命令。
        status, cmd_field = recv_bytes(connection, CMD_FIELD_LEN)

        if not status:
            print("status 为 false, 关闭连接 ...")
            connection.close()
            return
        
        # 将命令转换为我们的本地字节顺序。
        cmd = int.from_bytes(cmd_field, byteorder='big')

       
        if cmd != CMD["GET"]:
            print("没有收到GET CMD, 关闭连接 ...")
            connection.close()
            return

        # GET命令正确。读取文件名大小（字节）。
        status, filename_size_field = recv_bytes(connection, FILENAME_SIZE_FIELD_LEN)
        
        if not status:
            print("status 为 false, 关闭连接 ...")            
            connection.close()
            return
        
        filename_size_bytes = int.from_bytes(filename_size_field, byteorder='big')
        if not filename_size_bytes:
            print("file name size 为 0, 关闭连接 ...")
            connection.close()
            return
        
        print('文件名大小(数值表示为文件名长度) : ', filename_size_bytes)

        # 现在读取并解码请求的文件名。
        status, filename_bytes = recv_bytes(connection, filename_size_bytes)

        if not status:
            print("Closing connection ...")            
            connection.close()
            return
        
        if not filename_bytes:
            print("Connection is closed!")
            connection.close()
            return

        filename = filename_bytes.decode(MSG_ENCODING)
        print('客户端需求的 文件名 = ', filename)

        ################################################################
        # 查看是否能打开请求的文件。如果可以，发送它。
        
        # 如果找不到请求的文件，关闭连接并等待其他人。

        try:
            file = open(filename, 'r', encoding='utf-8').read()


        except FileNotFoundError:
            print(Server.FILE_NOT_FOUND_MSG)
            connection.close()                   
            return

        # 将文件内容编码成字节，记录其大小并生成用于传输的文件大小字段。
        file_bytes = file.encode(MSG_ENCODING)
        file_size_bytes = len(file_bytes)
        file_size_field = file_size_bytes.to_bytes(FILESIZE_FIELD_LEN, byteorder='big')

        # 创建带有头部字段的要发送的数据包。
        pkt = file_size_field + file_bytes
        
        try:
            # 向已连接的客户端发送数据包。
            connection.sendall(pkt)
            print("\n")
            print("发送packet")
            print("发送文件: ", filename)
            print("文件大小: ", file_size_field.hex(), "\n")

        except socket.error:

            # 如果客户端已关闭连接，则在这一端关闭套接字。
            print("Closing client connection ...")
            connection.close()
            return
        
        finally:
            connection.close()
            return


########################################################################
# CLIENT
########################################################################

class Client:

    RECV_SIZE = 10

    # Define the local file name where the downloaded file will be
    # saved.
    DOWNLOADED_FILE_NAME = "D:/McMaster/4DN4/lab3/client_recv/filedownload.txt"

    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.get_file()

    def get_socket(self):

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            exit()

    def connect_to_server(self):
        try:
            self.socket.connect((Server.HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            exit()


    def get_file(self):

        '''
        这段代码的主要功能是通过网络从服务器请求一个文件，并将接收到的文件内容保存到本地。过程包括创建并发送请求数据包，
        接收文件大小信息，然后根据文件大小接收文件内容，并将内容保存到本地文件中。
        如果在此过程中出现任何问题，如连接中断或文件接收不完整，程序将关闭连接并退出。
        '''
        
        '''
        创建各个字段, 需要这些字段才能发送
        '''

        cmd_field = CMD["GET"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        filename_field_bytes = Server.REMOTE_FILE_NAME.encode(MSG_ENCODING)
        filename_size_field = len(filename_field_bytes).to_bytes(FILENAME_SIZE_FIELD_LEN, byteorder='big')

        # 创建数据包。
        print("\n")
        print("创建packet")
        print("命令字段: ", cmd_field.hex())
        print("文件名大小(数值表示为文件名长度) :", filename_size_field.hex())
        print("文件名字段(字节形式下的实际文件名) :", filename_field_bytes.hex())
        
        pkt = cmd_field + filename_size_field + filename_field_bytes

        # 向服务器发送请求数据包。
        print("该packet发送给服务器...")
        self.socket.sendall(pkt)

        ################################################################
        # 处理服务器的文件传输响应
        print("\n")
        print("服务器正在相应......")
        print("\n")

        # 读取服务器返回的文件大小字段。
        status, file_size_bytes = recv_bytes(self.socket, FILESIZE_FIELD_LEN)

        if not status:
            print("Closing connection ...")            
            self.socket.close()
            return

        print("文件字段 : ", file_size_bytes.hex())
        
        if len(file_size_bytes) == 0:
            self.socket.close()
            return

        
        file_size = int.from_bytes(file_size_bytes, byteorder='big') # 确保以主机字节顺序解释它。
        print("文件大小(数值表示为文件长度) : ", file_size)

                             
        status, recvd_bytes_total = recv_bytes(self.socket, file_size)

        if not status:
            print("Closing connection ...")            
            self.socket.close()
            return

        try:
            # 使用接收到的文件名创建一个文件，并存储数据。
            print("Received {} bytes. Creating file: {}" \
                .format(len(recvd_bytes_total), Client.DOWNLOADED_FILE_NAME))

            with open(Client.DOWNLOADED_FILE_NAME, 'w', encoding='utf-8') as f:
                recvd_file = recvd_bytes_total.decode(MSG_ENCODING)
                f.write(recvd_file)
            print(recvd_file)
        except KeyboardInterrupt:
            print()
            exit(1)

            
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






