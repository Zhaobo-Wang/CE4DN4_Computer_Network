#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import struct

########################################################################
# Echo-Server class
########################################################################

class Server:

    HOST = "localhost"
    # HOST = "127.0.0.1"
    # HOST = ""
    # HOST = "0.0.0.0"
    PORT = 50000

    MSG = "Greetings! Thank-you for connecting!"

    RECV_SIZE = 256
    BACKLOG = 10
    MSG_ENCODING = "utf-8"

    def __init__(self):
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind( (Server.HOST, Server.PORT) )
            self.socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                self.connection_handler(self.socket.accept())
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
        print("Connection received from {}.".format(address_port))

        rx_data = connection.recv(Server.RECV_SIZE)
        unpacked_rx_data = struct.unpack('!hiq', rx_data)
        print("Received unpacked data: ", unpacked_rx_data)

########################################################################
# Echo-Client class
########################################################################

class Client:

    SERVER = "localhost"
    RECV_SIZE = 256
    
    # si, i, li = (32767, 2000, 987654321)

    si, i, li = (1, 2, 3)    
    PACKED_DATA = struct.pack('!hiq', si, i, li)

    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.connection_send()

    def get_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            sys.exit(1)


    def connect_to_server(self):
        try:
            self.socket.connect((Client.SERVER, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_send(self):
        try:
            self.socket.sendall(Client.PACKED_DATA)
        except Exception as msg:
            print(msg)
            sys.exit(1)

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






