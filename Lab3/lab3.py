import socket
import select
import sys
import threading
import argparse
import os


CMD_FIELD_LEN = 1 
FILENAME_SIZE_FIELD_LEN = 1 
FILESIZE_FIELD_LEN = 8 

CMD = {"GET": 1, "PUT": 2, "LIST": 3, "BYE": 5, "SCAN": 6, "CONNECT": 7}

MSG_ENCODING = "utf-8"
SOCKET_TIMEOUT = 4

def recv_bytes(sock, bytecount_target):

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
        # print("recv_bytes: socket timeout!")
        return (False, b'')

class Server:
    
    BROADCAST_PORT = 30000
    FILE_SHARING_PORT = 30001 
    broadcast_msg = "Zhaobo's File Sharing Service"
    RECV_BUFFER_SIZE = 1024
    MSG_ENCODING = "utf-8"

    FILE_NOT_FOUND_MSG = "Error: Requested file is not available!"
    REMOTE_FOLDER_LIST = "D:/McMaster/4DN4/lab3/server_send"
    MSG_ENCODING = "utf-8"
    MESSAGE =  "Lifeng's File Sharing Service"
    MESSAGE_ENCODED = MESSAGE.encode('utf-8')
    HOST = "0.0.0.0"        
    ADDRESS_PORT = (HOST, BROADCAST_PORT)

    def __init__(self):
        self.thread_list = []
        self.create_listen_sockets()
        #self.process_connections_forever()

    def create_listen_sockets(self):

        udp_thread = threading.Thread(target=self.start_udp_server)
        udp_thread.start()
        self.start_tcp_server()

    # Start the TCP server for file sharing
    def start_tcp_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.FILE_SHARING_PORT))
        server_socket.listen(5)
        server_socket.setblocking(0) 
        print(f"Listening for file sharing connections on port {self.FILE_SHARING_PORT}.")
        
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection received from {addr[0]} on port {addr[1]}.")
            client_thread = threading.Thread(target=self.handle_tcp_client, args=(client_socket,))
            client_thread.start()

    # Start the UDP server for service discovery
    def start_udp_server(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('', self.BROADCAST_PORT))
        print(f"Listening for service discovery messages on SDP port {self.BROADCAST_PORT}.")
        
        while True:
            data, addr = udp_socket.recvfrom(1024)
            if data.decode('utf-8') == "SERVICE DISCOVERY":
                response = self.SERVICE_NAME.encode('utf-8')
                udp_socket.sendto(response, addr)

        '''
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(Server.ADDRESS_PORT)
            
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind(('', self.FILE_SHARING_PORT))
            self.tcp_socket.listen(5)  
            self.tcp_socket.setblocking(0) 

            print(f"Server listening on UDP port: {self.BROADCAST_PORT} and TCP port: {self.FILE_SHARING_PORT}")
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
                            self.receive_forever()
                        elif s is self.tcp_socket:
                            client_tcp_socket, address = self.tcp_socket.accept()
                            client_thread = threading.Thread(target=self.handle_tcp_client, args=((client_tcp_socket, address),))
                            self.thread_list.append(client_thread)

                            # Start the new thread running.
                            # print("Starting serving thread: ", client_thread.name)
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
        '''

    def message_handler(self, data, address):
        message = data.decode(Server.MSG_ENCODING)
        print(f"Received from {address}: {message}")

        if message == "SERVICE DISCOVERY":
            self.udp_socket.sendto(self.SERVICE_NAME.encode(Server.MSG_ENCODING), address)
            print(f"Service name sent to {address}: {self.SERVICE_NAME}")

    def receive_forever(self):
        try:
            broadcast_msg, address = self.udp_socket.recvfrom(1024)
            if broadcast_msg.decode('utf-8') == "SERVICE DISCOVERY":
                self.udp_socket.sendto(Server.MESSAGE_ENCODED, address)
                print("Message received from {}.".format(address))
            print("Broadcast received: ", broadcast_msg.decode('utf-8'))
        except KeyboardInterrupt:
            print(); exit()
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def handle_tcp_client(self, client):

        connection, address = client

        print("\n")

        status, cmd_field = recv_bytes(connection, CMD_FIELD_LEN)

        '''
        if not status:
            print("Status false, closing connection ...")
            connection.close()
            return
        '''

        cmd = int.from_bytes(cmd_field, byteorder='big')

        if cmd == CMD["LIST"]:
            try:
                
                print("User try from server end: File Listing")

                files = os.listdir('D:/McMaster/4DN4/Lab3/server_send')
                file_list_str = '\n'.join(files)

                file_list_bytes = file_list_str.encode(MSG_ENCODING)
                file_list_size = len(file_list_bytes).to_bytes(FILESIZE_FIELD_LEN, byteorder='big')

                connection.sendall(file_list_size + file_list_bytes)
                print(f"File Listing sent to {address}")

            except Exception as e:

                print(f"Sending file_listing wrong: {e}")

        elif cmd == CMD["GET"]:

            print("User attempts to download file from server to client")

            status, filename_size_field = recv_bytes(connection, FILENAME_SIZE_FIELD_LEN)

            if not status:
                print("Failed to retrieve the size of the file to be downloaded, closing connection ...")            
                connection.close()
                return

            filename_size_bytes = int.from_bytes(filename_size_field, byteorder='big')

            if not filename_size_bytes:
                print("Failed to retrieve the size of the file to be downloaded, closing connection ...")
                connection.close()
                return
            
            print('Size of the filename (in bytes): ', filename_size_bytes)

            status, filename_bytes = recv_bytes(connection, filename_size_bytes)

            if not status:
                print("Failed to retrieve the filename to be downloaded, closing connection ...")            
                connection.close()
                return
            
            if not filename_bytes:
                print("Failed to retrieve the filename to be downloaded, closing connection ...")
                connection.close()
                return

            filename = filename_bytes.decode(MSG_ENCODING)
            print('Filename requested by client: ', filename)

            try:
                file = open(os.path.join('D:/McMaster/4DN4/Lab3/server_send', filename), 'r', encoding='utf-8').read()

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
                print("Sending packet...")
                print("Sending file: ", filename)
                print("File size: ", file_size_field.hex(), "\n")

            except socket.error:
                print("Closing client connection ...")
                connection.close()
                return
            
            finally:
                connection.close()
                return
            
        elif cmd == CMD["PUT"]:

            print("User attempts to upload file from client to server")

            status, filename_size_field = recv_bytes(connection, FILENAME_SIZE_FIELD_LEN)

            if not status:
                print("Failed to retrieve the size of the filename to be uploaded, closing connection ...")
                connection.close()
                return
            
            filename_size = int.from_bytes(filename_size_field, byteorder='big')
            status, filename_bytes = recv_bytes(connection, filename_size)

            if not status:
                print("Failed to retrieve the filename to be uploaded, closing connection ...")
                connection.close()
                return

            filename = filename_bytes.decode(MSG_ENCODING)

            print('Filename uploaded by client: ', filename)

            status, file_size_bytes = recv_bytes(connection, FILESIZE_FIELD_LEN)

            if not status:
                print("Failed to retrieve the size of the file to be uploaded, closing connection ...")
                connection.close()
                return

            file_size = int.from_bytes(file_size_bytes, byteorder='big')  
            print('File size received by server: ', file_size)

            status, file_data = recv_bytes(connection, file_size)
            if not status:
                print("Failed to retrieve the file data to be uploaded, closing connection ...")
                connection.close()
                return

            try:
                with open(os.path.join('D:/McMaster/4DN4/Lab3/server_send', filename), 'wb') as f:
                    f.write(file_data)
                print("File successfully uploaded to server and saved.")
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
            print("Unknown command")
            connection.close()


#################################################################################
            

class Client:

    SERVER_HOSTNAME = "localhost"
    RECV_BUFFER_SIZE = 1024
    local_Client_File_LIST = "D:/McMaster/4DN4/Lab3/client_recv"
    DOWNLOADED_FILE_NAME = "D:/McMaster/4DN4/lab3/client_recv/filedownload_3_server.txt"
    UPLOADED_FILE_NAME = "D:/McMaster/4DN4/Lab3/client_recv/upload_file_1_client.txt"
    MSG_ENCODING = "utf-8"
    MESSAGE =  "SERVICE DISCOVERY"
    MESSAGE_ENCODED = MESSAGE.encode('utf-8')
    BROADCAST_ADDRESS = "255.255.255.255"
    SDP = 30000
    ADDRESS_PORT = (BROADCAST_ADDRESS, SDP)

    def __init__(self):
        #self.send_service_discovery_request()
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
        UDP_broadcast_socket.bind(("192.168.40.83",30003))
        UDP_broadcast_socket.settimeout(10)  
        discovery_message = "SERVICE DISCOVERY"
        #UDP_broadcast_socket.sendto(discovery_message.encode('utf-8'), ('255.255.255.255', Server.BROADCAST_PORT))
        print(f"Sent SERVICE DISCOVERY request via UDP broadcast.")
        
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
                    print("Invalid input. Please use the format")

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


        print("\nCreating packet")
        print("Command field: ", cmd_field.hex())
        print("Filename size (as byte length): ", filename_size_field.hex())
        print("Filename field (in byte form): ", filename_field_bytes.hex())
        

        pkt = cmd_field + filename_size_field + filename_field_bytes


        print("Sending packet to server...")
        self.socket.sendall(pkt)


        print("\nWaiting for server response...\n")
        status, file_size_bytes = recv_bytes(self.socket, FILESIZE_FIELD_LEN)

        if not status:
            # print("Closing connection ...")
            self.socket.close()
            return

        print("File size field: ", file_size_bytes.hex())
        
        if len(file_size_bytes) == 0:
            self.socket.close()
            return

        file_size = int.from_bytes(file_size_bytes, byteorder='big') 
        print("File size (as byte length): ", file_size)
                                

        status, recvd_bytes_total = recv_bytes(self.socket, file_size)

        if not status:
            # print("Closing connection ...")            
            self.socket.close()
            return


        try:
            print(f"Received {len(recvd_bytes_total)} bytes. Creating file: {filename}")

            with open(filename, 'wb') as f:  
                f.write(recvd_bytes_total)  

            print("File successfully downloaded and saved.")

        except KeyboardInterrupt:
            print("Download interrupted by user.")
            exit(1)


    def remote_list_files(self):

        cmd_field = CMD["LIST"].to_bytes(CMD_FIELD_LEN, byteorder='big')


        print("Creating 'list' packet")
        print("Command field: ", cmd_field.hex())
        self.socket.sendall(cmd_field)
        print("Waiting for server response...")

        status, list_size_bytes = recv_bytes(self.socket, FILESIZE_FIELD_LEN)

        if not status:
            # print("Closing connection ...")
            self.socket.close()
            return

        if len(list_size_bytes) == 0:
            print("No data received, closing connection...")
            self.socket.close()
            return

        list_size = int.from_bytes(list_size_bytes, byteorder='big')
        print("Received file list size: ", list_size)
        print("\n")

        status, file_list_bytes = recv_bytes(self.socket, list_size)

        if not status:
            # print("Closing connection ...")
            self.socket.close()
            return

        try:

            file_list_str = file_list_bytes.decode(MSG_ENCODING)
            print(f"Here is the file list from the server folder {Server.REMOTE_FOLDER_LIST}:")
            print(file_list_str)

        except Exception as e:
            print("Error:", e)


    def put_files(self, filename):

        if not os.path.exists(filename):
            print("File does not exist.")
            return

        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()

        cmd_field = CMD["PUT"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        filename_field_bytes = os.path.basename(filename).encode(MSG_ENCODING)

        filename_size_field = len(filename_field_bytes).to_bytes(FILENAME_SIZE_FIELD_LEN, byteorder='big')
        file_content_bytes = file_content.encode(MSG_ENCODING)
        file_size_field = len(file_content_bytes).to_bytes(FILESIZE_FIELD_LEN, byteorder='big')


        print("Creating 'put' packet")
        print("Command field: ", cmd_field.hex())
        print("Filename size (as byte length): ", filename_size_field.hex())
        print("Filename field (in byte form): ", filename_field_bytes.hex())
        print("File size (as byte length): ", file_size_field.hex())

        pkt = cmd_field + filename_size_field + filename_field_bytes + file_size_field + file_content_bytes

        print("Sending 'put' packet to server...")
        self.socket.sendall(pkt)

        print("Waiting for server response...")
        print("File successfully upload to server")

        status, response = recv_bytes(self.socket, Client.RECV_BUFFER_SIZE)

        if not status:
            # print("Closing connection ...")
            self.socket.close()
            return

        print("Response from server: ", response.decode(MSG_ENCODING))

    def local_list_files(self):

        '''
        cmd_field = CMD["lLIST"].to_bytes(CMD_FIELD_LEN, byteorder='big')

        print("\n")
        print("Creating 'llist' packet")
        print("Command field: ", cmd_field.hex())


        self.socket.sendall(cmd_field)   
        '''

        try:
            files = os.listdir(Client.local_Client_File_LIST)
            file_list_str = '\n'.join(files)
            print("\n")
            print(f"Here is the file list from the client folder {Client.local_Client_File_LIST}:")
            print(file_list_str)

        except Exception as e:

            print("Error:", e)

    def bye(self):
        try:
            
            print("Sending BYE message to server...")
            cmd_field = CMD["BYE"].to_bytes(CMD_FIELD_LEN, byteorder='big')  
            self.socket.sendall(cmd_field)

            print("Closing socket...")
            self.socket.close()

        except Exception as e:

            print("An error occurred while closing the connection:", e)

        finally:
            self.socket.close()

    def connect(self):

        try:
            
            print(f"Connected to {Client.SERVER_HOSTNAME} on port {Server.FILE_SHARING_PORT}")            
            cmd_field = CMD["CONNECT"].to_bytes(CMD_FIELD_LEN, byteorder='big')  
            self.socket.sendall(cmd_field)

        except Exception as e:

            print("An error occurred in connection:", e)


    def message_receive(self):
        try:
            # recvfrom returns bytes received and the identity of the
            # sender.
            recvd_bytes, address = self.socket.recvfrom(1024)
            # print("Received Message Bytes: ", recvd_bytes)
            print(f"{recvd_bytes.decode(Server.MSG_ENCODING)} found at {address}" )
        except socket.timeout:
            print("No service found")
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def scan(self):
        print("Broadcasting to {} ...".format(Client.ADDRESS_PORT))
        self.socket.sendto(Client.MESSAGE_ENCODED, Client.ADDRESS_PORT)
        self.message_receive()

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
