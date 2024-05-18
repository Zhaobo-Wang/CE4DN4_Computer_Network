import socket
import select
import sys
import threading
import argparse
import os


CMD_FIELD_LEN            = 1 
FILENAME_SIZE_FIELD_LEN  = 1 
FILESIZE_FIELD_LEN       = 8 

CMD = {"GET": 1, "PUT": 2, "LIST": 3, "BYE": 5, "SCAN": 6, "CONNECT": 7}
#User会使用上面的COMMAND，进行request from server

MSG_ENCODING = "utf-8"
SOCKET_TIMEOUT = 4

def recv_bytes(sock, bytecount_target):

    '''
    总结来说, recv_bytes 函数确保
    能从socket中接收到完整的、指定数量的数据,
    这对于网络通信中确保数据完整性非常重要。
    '''

    sock.settimeout(SOCKET_TIMEOUT)

    try:
        byte_recv_count = 0 
        recv_bytes = b''
        
        while byte_recv_count < bytecount_target:
            new_bytes = sock.recv(bytecount_target-byte_recv_count)

            if not new_bytes:
                return(False, b'')
            
            byte_recv_count += len(new_bytes)
            recv_bytes += new_bytes
            
        sock.settimeout(None)            
        return (True, recv_bytes)
    
    except socket.timeout:
        sock.settimeout(None)        
        print("recv_bytes: socket timeout!")
        return (False, b'')

class Server:

    SERVICE_DISCOVERY_PORT = 30000
    FILE_SHARING_PORT = 30001 
    SERVICE_NAME = "Zhaobo's File Sharing Service"
    RECV_BUFFER_SIZE = 1024
    MSG_ENCODING = "utf-8"

    FILE_NOT_FOUND_MSG = "Error: Requested file is not available!"
    REMOTE_FOLDER_LIST = "D:/McMaster/4DN4/lab3/server_send"

    def __init__(self):
        self.thread_list = []
        self.create_listen_sockets()
        self.process_connections_forever()

    def create_listen_sockets(self):

        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('', self.SERVICE_DISCOVERY_PORT))
            
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind(('', self.FILE_SHARING_PORT))
            self.tcp_socket.listen(5)  
            self.tcp_socket.setblocking(0) 

            print(f"Server listening on UDP port: {self.SERVICE_DISCOVERY_PORT} and TCP port: {self.FILE_SHARING_PORT}")
        except Exception as msg:
            print(msg)
            sys.exit(1)
            
    def process_connections_forever(self):
        try:
            inputs = [self.udp_socket, self.tcp_socket]
            while True:
                readable, _, _ = select.select(inputs, [], [], 1)
                for s in readable:
                    if s is self.udp_socket:
                        data, address = self.udp_socket.recvfrom(Server.RECV_BUFFER_SIZE)
                        self.message_handler(data, address)
                    elif s is self.tcp_socket:
                        client_tcp_socket, address = self.tcp_socket.accept()
                        client_thread = threading.Thread(target=self.handle_tcp_client, args=((client_tcp_socket, address),))
                        self.thread_list.append(client_thread)

                        # Start the new thread running.
                        #print("Starting serving thread: ", client_thread.name)
                        client_thread.daemon = True
                        client_thread.start()

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            print("Closing sockets ...")
            self.udp_socket.close()
            self.tcp_socket.close()
            sys.exit(1)

    def message_handler(self, data, address):
        message = data.decode(Server.MSG_ENCODING)
        print(f"From {address} received: {message}")

        if message == "SERVICE DISCOVERY":
            self.udp_socket.sendto(self.SERVICE_NAME.encode(Server.MSG_ENCODING), address)
            print("UDP scan")
            print(f"Sent to {address} service name: {self.SERVICE_NAME}")

    def handle_tcp_client(self, client):

        connection, address = client

        print("\n")

        status, cmd_field = recv_bytes(connection, CMD_FIELD_LEN)

        if not status:
            print("没收到COMMAND或status为False, 关闭连接 ...")
            connection.close()
            return
        
        cmd = int.from_bytes(cmd_field, byteorder='big')


        if cmd == CMD["LIST"]:
            
            print("该用户尝试从server端: File Listing")

            try:

                files = os.listdir('D:/McMaster/4DN4/Lab3/server_send')
                each_file_name = '\n'.join(files)

                file_list_bytes = each_file_name.encode(MSG_ENCODING)  
                # 将文件列表字符串编码成字节
                file_list_size = len(file_list_bytes).to_bytes(FILESIZE_FIELD_LEN, byteorder='big')  
                # 将文件列表的大小转换成字节

                # 发送文件列表大小以及文件列表
                connection.sendall(file_list_size + file_list_bytes)
                print(f"向 {address} 发送了 File Listing")

            except Exception as e:

                print(f"发送文件列表时出错: {e}")  

        elif cmd == CMD["GET"]:

            print("该用户尝试从Server端 Download File 至Client端")

            status, filename_size_field = recv_bytes(connection, FILENAME_SIZE_FIELD_LEN)
        
            if not status:
                print("无法获取所需要下载的文件大小, 关闭连接 ...")            
                connection.close()
                return
        
            filename_size_bytes = int.from_bytes(filename_size_field, byteorder='big')

            if not filename_size_bytes:
                print("无法获取所需要下载的文件大小, 关闭连接 ...")
                connection.close()
                return
            
            print('文件名大小(数值表示为文件名长度) : ', filename_size_bytes)

            status, filename_bytes = recv_bytes(connection, filename_size_bytes)

            if not status:
                print("无法获取所需要下载的文件名, 关闭连接 ...")            
                connection.close()
                return
            
            if not filename_bytes:
                print("无法获取所需要下载的文件名, 关闭连接 ...")
                connection.close()
                return

            filename = filename_bytes.decode(MSG_ENCODING)
            print('Client端需求的文件名 = ', filename)

            try:
                file = open(filename, 'r', encoding='utf-8').read()


            except FileNotFoundError:
                print(Server.FILE_NOT_FOUND_MSG)
                connection.close()                   
                return

            file_bytes = file.encode(MSG_ENCODING)
            file_size_bytes = len(file_bytes)
            file_size_field = file_size_bytes.to_bytes(FILESIZE_FIELD_LEN, byteorder='big')

            pkt = file_size_field + file_bytes
            
            try:
                connection.sendall(pkt)
                print("发送packet...")
                print("发送文件: ", filename)
                print("文件大小: ", file_size_field.hex())
                print("用户下载文件完成")

            except socket.error:
                print("Closing client connection ...")
                connection.close()
                return
            
            finally:
                connection.close()
                return
            
        elif cmd == CMD["PUT"]:

            print("该用户尝试从client端 Upload File 至Server端")

            # 接收文件名长度和文件名

            status, filename_size_field = recv_bytes(connection, FILENAME_SIZE_FIELD_LEN)

            if not status:
                print("无法获取所需要上传的文件名大小, 关闭连接 ...")
                connection.close()
                return
            
            filename_size = int.from_bytes(filename_size_field, byteorder='big')
            status, filename_bytes = recv_bytes(connection, filename_size)

            if not status:
                print("无法获取所需要上传的文件名, 关闭连接 ...")
                connection.close()
                return

            filename = filename_bytes.decode(MSG_ENCODING)

            print('客户端上传的文件名: ', filename)

            # 接收文件大小和文件内容
            status, file_size_bytes = recv_bytes(connection, FILESIZE_FIELD_LEN)

            if not status:
                print("无法获取所需要上传的文件大小, 关闭连接 ...")
                connection.close()
                return

            file_size = int.from_bytes(file_size_bytes, byteorder='big')  
            print('Server收到的文件大小: ', file_size)

            status, file_data = recv_bytes(connection, file_size)
            if not status:
                print("无法获取所需要上传的文件数据, 关闭连接 ...")
                connection.close()
                return

            # 将接收到的文件内容写入文件
            try:
                with open(os.path.join('D:/McMaster/4DN4/Lab3/server_send', filename), 'wb') as f:
                    f.write(file_data)
                print("文件上传到server成功并保存.")
            except Exception as e:
                print(f"Error saving file: {e}")            

        elif cmd == CMD["BYE"]:

            print("Received BYE command from client")
            connection.sendall("Connection closed".encode('utf-8'))

        elif cmd == CMD["CONNECT"]:

            print(f"Listening for file sharing connections on port {Server.FILE_SHARING_PORT}")

        elif cmd == CMD["SCAN"]:

            print("scan")

        else:
            print("不知道这个COMMAND, 关闭socket...")
            connection.close()

#################################################################################
            

class Client:

    SERVER_HOSTNAME = "localhost"
    RECV_BUFFER_SIZE = 1024
    local_Client_File_LIST = "D:/McMaster/4DN4/Lab3/client_recv"
    DOWNLOADED_FILE_NAME = "D:/McMaster/4DN4/lab3/client_recv/filedownload_3_server.txt"
    UPLOADED_FILE_NAME = "D:/McMaster/4DN4/Lab3/client_recv/upload_file_1_client.txt"

    def __init__(self):
        self.send_service_discovery_request()
        self.connect_to_server()
        self.send_console_input_forever()

    def connect_to_server(self):

        try:

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect((Client.SERVER_HOSTNAME, Server.FILE_SHARING_PORT)) 

        except Exception as e:

            print(f"Cannot connect to the server: {e}")
            sys.exit(1)

    def send_service_discovery_request(self): 

        UDP_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        UDP_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        UDP_broadcast_socket.settimeout(10)  
        discovery_message = "SERVICE DISCOVERY"
        UDP_broadcast_socket.sendto(discovery_message.encode('utf-8'), ('255.255.255.255', Server.SERVICE_DISCOVERY_PORT))
        print(f" 发送SERVICE DISCOVERY请求通过UDP广播 ")

        try:

            while True:
                data, addr = UDP_broadcast_socket.recvfrom(1024)
                print(f"Received response from {addr}: {data.decode()}")
                break  

        except socket.timeout:
            print("Service discovery timed out. No response received.")

        finally:
            UDP_broadcast_socket.close()

    def get_console_input(self):
        while True:
            self.input_text = input("Input: ")
            self.command_parts = self.input_text.strip().split(' ')
            if self.input_text != "":
                break
    
    def send_console_input_forever(self):
        should_exit = False 

        while not should_exit:  

            try:

                self.get_console_input()
                self.connect_to_server() 

                if self.command_parts[0].upper() == "GET" and len(self.command_parts) == 2:
                    download_filename = self.command_parts[1]
                    self.get_file(download_filename)

                elif self.input_text.upper() == "RLIST":
                    self.remote_list_files()

                elif self.input_text.upper() == "LLIST":
                    self.local_list_files()

                elif self.command_parts[0].upper() == "PUT" and len(self.command_parts) == 2:
                    upload_filename = self.command_parts[1]
                    self.put_files(upload_filename)

                elif self.input_text.upper() == "BYE":
                    self.bye()  
                    should_exit = True  

                elif self.input_text.upper() == "SCAN":
                    self.scan()

                elif self.input_text.upper() == "CONNECT":
                    self.connect()

                else:
                    print("COMMAND 格式不对")

                if not should_exit:  
                    self.socket.close() 

            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                if self.socket:
                    self.socket.close()
                should_exit = True  

            if should_exit:  
                if self.socket:
                    self.socket.close()
                print("Exiting...")
                sys.exit(1)

                
    def connection_send(self):
        try:
            self.socket.sendall(self.input_text.encode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))

        except Exception as msg:
            print(msg)
            sys.exit(1)
    
    def get_file(self, filename):

        cmd_field = CMD["GET"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        filename_field_bytes = filename.encode(MSG_ENCODING)
        filename_size_field = len(filename_field_bytes).to_bytes(FILENAME_SIZE_FIELD_LEN, byteorder='big')

        # 创建数据包。
        print("\n创建packet")
        print("命令字段: ", cmd_field.hex())
        print("文件名大小(数值表示为文件名长度) :", filename_size_field.hex())
        print("文件名字段(字节形式下的实际文件名) :", filename_field_bytes.hex())
        
        pkt = cmd_field + filename_size_field + filename_field_bytes

        # 向服务器发送请求数据包。
        print("该packet发送给服务器...")
        self.socket.sendall(pkt)

        print("\n服务器正在相应......")
        status, file_size_bytes = recv_bytes(self.socket, FILESIZE_FIELD_LEN)

        if not status:          
            self.socket.close()
            return

        print("文件字段 : ", file_size_bytes.hex())
        
        if len(file_size_bytes) == 0:
            self.socket.close()
            return

        file_size = int.from_bytes(file_size_bytes, byteorder='big') 
        print("文件大小(数值表示为文件长度) : ", file_size)

                             
        status, recvd_bytes_total = recv_bytes(self.socket, file_size)

        if not status:         
            self.socket.close()
            return

        try:
            print(f"收到 {len(recvd_bytes_total)} 字节. 创建文件: {filename}")

            with open(filename, 'wb') as f:  
                f.write(recvd_bytes_total)  

            print("文件下载并保存成功")

        except KeyboardInterrupt:
            print("Download interrupted by user.")
            exit(1)

    def put_files(self,filename):
        # 确认文件存在
        if not os.path.exists(filename):
            print("文件不存在.")
            return

        # 获取文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # 准备数据包
        cmd_field = CMD["PUT"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        filename_field_bytes = os.path.basename(filename).encode(MSG_ENCODING)
        filename_size_field = len(filename_field_bytes).to_bytes(FILENAME_SIZE_FIELD_LEN, byteorder='big')
        file_content_bytes = file_content.encode(MSG_ENCODING)
        file_size_field = len(file_content_bytes).to_bytes(FILESIZE_FIELD_LEN, byteorder='big')

        # 创建数据包
        print("创建 'put' packet")
        print("命令字段: ", cmd_field.hex())
        print("文件名大小(数值表示为文件名长度) :", filename_size_field.hex())
        print("文件名字段(字节形式下的实际文件名) :", filename_field_bytes.hex())
        print("文件大小(数值表示为文件长度) :", file_size_field.hex())

        pkt = cmd_field + filename_size_field + filename_field_bytes + file_size_field + file_content_bytes

        # 向服务器发送请求数据包
        print("'put' packet发送给服务器...")
        self.socket.sendall(pkt)

        print("等待服务器响应...")

        # 接收服务器响应（这里假设服务器会发送一些类型的确认消息）
        status, response = recv_bytes(self.socket, Client.RECV_BUFFER_SIZE)
        if not status:
            print("Closing connection ...")
            self.socket.close()
            return

        print("从服务器接收的响应: ", response.decode(MSG_ENCODING))


    def remote_list_files(self):
       
        cmd_field = CMD["LIST"].to_bytes(CMD_FIELD_LEN, byteorder='big')  # 假定你已经定义了 CMD 字典和 CMD_FIELD_LEN

        # 向服务器发送请求数据包
        print("创建 rLIST packet")
        print("命令字段: ", cmd_field.hex())
        self.socket.sendall(cmd_field)
        print("服务器正在响应...")

        # 首先接收服务器回复的列表大小
        status, list_size_bytes = recv_bytes(self.socket, FILESIZE_FIELD_LEN)  # 假定 FILESIZE_FIELD_LEN 是定义好的列表大小字段长度

        if not status:
            self.socket.close()
            return

        if len(list_size_bytes) == 0:
            print("没有接收到数据，关闭连接...")
            self.socket.close()
            return

        list_size = int.from_bytes(list_size_bytes, byteorder='big')
        print("接收到的文件列表大小: ", list_size)
        print("\n")

        # 然后接收实际的文件列表
        status, file_list_bytes = recv_bytes(self.socket, list_size)

        if not status:
            self.socket.close()
            return

        try:

            file_list_str = file_list_bytes.decode(MSG_ENCODING)  # 假定你已经定义了 MSG_ENCODING
            print(f"以下是server端传回来的文件夹 {Server.REMOTE_FOLDER_LIST}:")
            print(file_list_str)  # 打印出服务器返回的文件列表
        except Exception as e:
            print("Error:", e)

    
    def local_list_files(self):

        '''
        cmd_field = CMD["lLIST"].to_bytes(CMD_FIELD_LEN, byteorder='big')  # 假定你已经定义了 CMD 字典和 CMD_FIELD_LEN
        
        # 向服务器发送请求数据包
        print("创建 lLIST packet")
        print("命令字段: ", cmd_field.hex())
               
        self.socket.sendall(cmd_field)
        '''

        try:
            files = os.listdir(Client.local_Client_File_LIST)
            file_list_str = '\n'.join(files)
            print("\n")
            print(f"以下是client端的本地文件夹 {Client.local_Client_File_LIST}:")
            print(file_list_str)
        except Exception as e:
            print("Error:", e)

    def bye(self):
        try:
            
            print("尝试离开服务器...")
            cmd_field = CMD["BYE"].to_bytes(CMD_FIELD_LEN, byteorder='big')  
            self.socket.sendall(cmd_field)

            print("关闭连接...")
            self.socket.close()

        except Exception as e:

            print("关闭时产生问题:", e)

        finally:
            self.socket.close()

    def connect(self):

        try:
            
            print(f"Connected to {Client.SERVER_HOSTNAME} on port {Server.FILE_SHARING_PORT}")            
            cmd_field = CMD["CONNECT"].to_bytes(CMD_FIELD_LEN, byteorder='big')  
            self.socket.sendall(cmd_field)

        except Exception as e:

            print("An error occurred while closing the connection:", e)

    def scan(self):

        print("scan")

########################################################################
# Process command line arguments if run directly.
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
