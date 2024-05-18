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
                if len(parts) != 4:
                    logging.warning("Invalid makeroom command format")
                    return "Invalid makeroom command. Usage: makeroom <name> <address> <port>"

                room_name, address, port = parts[1], parts[2], parts[3]
                
                if not (239 <= int(address.split('.')[0]) <= 239):
                    logging.error("Invalid multicast address: %s", address)
                    return "Invalid multicast address. Must be in the range 239.0.0.0 to 239.255.255.255"
                
                for room in self.chat_rooms.values():
                    if room['address'] == address and room['port'] == port:
                        logging.error("Address and port combination already in use")
                        return "Address and port combination is already in use for another chat room."

                # Check if the chat room name already exists
                if room_name in self.chat_rooms:
                    logging.warning("Attempt to create a room that already exists: %s", room_name)
                    return "Chat room already exists."

                self.chat_rooms[room_name] = {'address': address, 'port': port}
                logging.info("Create chat room: %s", room_name)
                return f"Chat room {room_name} created with address {address} and port {port}"

        
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
            
        elif cmd == 'getinfo':
            room_name = parts[1]
            if room_name in self.chat_rooms:
                info = self.chat_rooms[room_name]
                return f"{info['address']} {info['port']}"
            else:
                return "Chat room not found"
            
        elif cmd == 'bye':
            logging.info("Client has disconnected.")
            return "Client disconnected"
        
        else:
            logging.error("Invalid command: %s", cmd)
            return "Invalid command"

#####################################################################################################################################        

class Client:
    multicast_address = "239.0.0.1" 
    multicast_port = 5000 
    exit_chat = "exit_chat"
    chat_name = "Anonymous"  


    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 5000
        self.prompt = "Enter Command > "
        self.in_chat_mode = False
        self.multicast_socket = None
        self.receiving_thread = None
        self.chat_room_name = ""
        self.start()

    def start(self):
        while True:
            command = input(self.prompt)
            if command.startswith('connect'):
                _, ip, port = command.split()
                self.connect(ip, int(port))
            elif command.startswith('chat'):
                _, chat_room_name = command.split()
                self.start_chat(chat_room_name)
            elif command.startswith('name'):
                _, name = command.split(maxsplit=1)  
                #print("name")
                self.set_name(name)
            elif self.in_chat_mode:
                if command == Client.exit_chat:
                    self.stop_chat()
                    self.leave_chat_room()
                    self.in_chat_mode= False
                else:
                    self.send_multicast_message(command)
            else:    
                self.send_message(command)

    def connect(self, server_ip, server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(8)
        self.client_socket.connect((server_ip,server_port))
        self.prompt = "Connected >>>"

    def get_chat_room_info(self, chat_room_name):
        try:
            self.send_message(f"getinfo {chat_room_name}")
            response = self.client_socket.recv(1024).decode()
            return response
        except Exception as e:
            print(f"Error in get_chat_room_info: {e}")
            return "" 

    def set_name(self, name):
        Client.chat_name = name
        print("Change name successfully")

    def start_chat(self, chat_room_name):
        self.chat_room_name = chat_room_name 
        #info = self.get_chat_room_info(chat_room_name)  
        #print(info)
        #if info != "Chat room not found.":
        self.join_chat_room(chat_room_name, Client.multicast_address, Client.multicast_port)
        self.in_chat_mode = True
        self.prompt = f"({chat_room_name}'s - chatroom) > "
        print("Entered chat mode.")
        self.receiving_thread = threading.Thread(target=self.receive_multicast_messages)
        self.receiving_thread.start()

    
    def stop_chat(self):
        self.in_chat_mode = False
        self.prompt = "Enter Command > "
        self.leave_chat_room()
        #if self.receiving_thread is not None:
        #    self.receiving_thread.join() 
        print("Exited chat mode.")


    def join_chat_room(self, chat_room_name, multicast_address, multicast_port):
        print("join chat room")
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        
        self.multicast_socket.bind(('', multicast_port))         
        mreq = struct.pack("4sl", socket.inet_aton(multicast_address), socket.INADDR_ANY)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


    
    def leave_chat_room(self):
        if self.multicast_socket:
            self.multicast_socket.close()
            self.multicast_socket = None

    def send_multicast_message(self, message):
        if not self.in_chat_mode or not self.multicast_socket:
            print("Not in chat mode or not connected to a chat room.")
            return       
        message_to_send = f"{self.chat_name}: {message}"        
        try:
            self.multicast_socket.sendto(message_to_send.encode(), (self.multicast_address, self.multicast_port))
            #print("Message sent.")
        except socket.error as e:
            print(f"Error sending multicast message: {e}")

    
    def receive_multicast_messages(self):
        while self.in_chat_mode and self.multicast_socket:
            try:
                data, _ = self.multicast_socket.recvfrom(1024)
                print(f"\n {data.decode()}\n{self.prompt}", end='')
            except socket.error as e:
                print(f"Exit chat and multicast socket being exit: {e}")
                break

    def send_message(self, command):
        try:
            self.client_socket.sendall(command.encode())
            if command == 'bye':
                self.prompt = "Enter Command >"
                self.client_socket.close()
                return 
        except Exception as e:
            print(f"Error sending message: {e}")
            return

        try:
            response = self.client_socket.recv(1024).decode()
            print(response)
        except Exception as e:
            print(f"Error receiving response: {e}")



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
