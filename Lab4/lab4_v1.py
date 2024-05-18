import socket
import threading
import argparse
import logging
import struct

class Server:

    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 5000 
        self.chat_rooms = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_server()


    def start_server(self):
        try:
            self.server_socket.bind((self.host,self.port))
            self.server_socket.listen(5)
            logging.info("CRDS is listening on port: %s", self.port)
            
            while True:
                client_socket, addr = self.server_socket.accept()
                logging.info("Connected to %s: %s", *addr)
                threading.Thread(target = self.handle_client, args=(client_socket,)).start()
        except Exception as e:
            logging.error("An error occurred while starting the server: %s", e)


    def handle_client(self, client_socket):
        try:
            while True:
                command = client_socket.recv(1024).decode()
                if not command:
                    break
                response = self.execute_command(command)
                client_socket.send(response.encode())
        except Exception as e:
            logging.error("An error occured in client handling: %s", e)
        finally:
            client_socket.close()

    def execute_command(self,command):
        parts = command.split()
        cmd = parts[0]

        logging.info("Received command: %s", command)

        if cmd == "getdir":
            logging.info("Returning chat room directory")
            return str(self.chat_rooms)
        
        elif cmd == "makeroom":
            if len(parts) !=4:
                logging.warning("Invalid makeroom command format")
                return "Invalid makeroom command. Usage: makeroom <name> <address> <port>"

            room_name, address, port = parts[1], parts[2], parts[3]
            if not (239 <= int(address.split('.')[0]) <= 239):
                logging.error("Invalid multicast address: %s", address)
                return "Invalid multicast address. Must be in the range 239.0.0.0 to 239.255.255.255"
            
            if room_name in self.chat_rooms:
                logging.warning("Attempt to create a room that already exists: %s", room_name)
                return "Chat room already exists."
            
            self.chat_rooms[room_name] = {'address': address, 'port': port}
            logging.info("Create chat room: %s", room_name)
            return f"Chat room {room_name} create with address {address} and port {port}"
        
        elif cmd == 'deleteroom':
            if len(parts) !=2:
                logging.warning("Invalid deleteroom command format")
                return " Invalid deleteroom command. Usage: deleteroom <name>"
            
            room_name = parts[1]

            if room_name in self.chat_rooms:
                del self.chat_rooms[room_name]

                logging.info("Deleted chat room: %s", room_name)
                return f"Chat room {room_name} deleted"
            
            else:
                logging.warning("Attempt to delete a non-existing room: %s", room_name)
                return "Chat room not found"
        else:
            logging.error("Invalid command: %s", cmd)
            return "Invalid command"

class Client:
    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 5000
        self.prompt = ">"
        self.start()


    def send_message(self,command):
        self.client_socket.sendall(command.encode())
        response = self.client_socket.recv(1024).decode()
        print(response)

    def start(self):
        while True:
            command = input("Enter command: ")
            if command.startswith('connect'):
                _, ip, port = command.split()
                self.connect(ip, int(port))
            elif command == 'bye':
                self.disconnect()
            elif command.startswith('name'):
                _, name = command.split()
                self.set_name(name)
            elif self.in_chat_mode:
                self.send_chat_message(command)
            elif command.startswith('chat'):
                _, chat_room_name = command.split()
                self.start_chat(chat_room_name)
            elif command == '<ctrl>]':
                self.stop_chat()
            else:    
                self.send_message(command)

    def connect(self, server_ip, server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip,server_port))
        self.prompt = "(connected) >"

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
        self.client_socket = None
        self.prompt = ">"

    def set_name(self, name):
        self.chat_name = name

    def start_chat(self, chat_room_name):
        self.prompt = f"(chat - {chat_room_name})"
    
    def stop_chat(self):
        self.prompt = "(connected) > "
    '''
    多播就像是广播，可以选择特定的接受群体，而不是发送给所有人

    多播的应用

    在一个聊天室应用中，多播非常有用，当一个用户发送消息时，
    这个消息可以迅速被发放给聊天室中的所有其他用户
    
    '''
    def join_chat_room(self, chat_room_name):
        multicast_address = '239.0.0.1'
        multicast_port = 5000

        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.multicast_socket.bind(('',multicast_port))
        '''
        创建了一个多播请求
        结构包含两个部分
        { 多播组的IP地址，本地接口的IP地址 }
        INADDR_ANY 表示客户端不指定使用哪个网络接口进行多播，让操作系统自动选择
        '''
        multicast_req = struct.pack("4sl", socket.inet_aton(multicast_address), socket.INADDR_ANY)
        '''
        加入多播组
        '''
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_req)
        '''
        接收线程处理多播消息
        '''
        threading.Thread(target=self.receive_multicast_messages, args=()).start()
    
    def leave_chat_room(self):
        if self.multicast_socket:
            self.multicast_socket.close()
            self.multicast_socket = None
    
    def receive_multicast_messages(self):
        while self.multicast_socket:
            try:
                data,_ = self.multicast_socket.recvfrom(1024)
                print(f"Received message: {data.decode()}")
            except socket.error:
                break

            
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s',
                    handlers=[
                        logging.FileHandler("server.log"),
                        logging.StreamHandler()
                    ])

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()
