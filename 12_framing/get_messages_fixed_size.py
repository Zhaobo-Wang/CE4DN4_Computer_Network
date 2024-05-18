#!/usr/bin/env python3

########################################################################
# GET Messages
#
# In this version, the message lengths are assumed to be known in
# advance so the client knows exactly how many bytes to read in the
# response. The server randomly selects from a set of messages to
# respond with.
#
########################################################################

import socket
import argparse
import time
import sys
import StringSamples
import random

from RecvBytes import *

MSG_ENCODING = 'utf-8'

GET_REQUEST = 'GET'
GET_REQUEST_SIZE = len(GET_REQUEST)

GET_REQUEST_BYTES = GET_REQUEST.encode(MSG_ENCODING)
GET_REQUEST_BYTES_SIZE = len(GET_REQUEST_BYTES)

########################################################################
# SERVER
########################################################################

class Server:

    HOSTNAME = socket.gethostname()
    PORT = 50000

    RECV_SIZE = 1024

    BACKLOG = 5

    # Define a list of messages. When a client sends a "GET", select
    # one randomly and return it.

    MSG_SIZE = 72

    MSG_LIST = [
    "1" * MSG_SIZE,
    "2" * MSG_SIZE,
    "3" * MSG_SIZE,
    ]

#    MSG_LIST = [
#    "1" * MSG_SIZE,
#    "2" * MSG_SIZE,
#    "3" * MSG_SIZE,
#    "λ" * MSG_SIZE
#    ]
    
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

        # If we have a valid request message ('GET' string), then send
        # an encoded message and continue listening to the
        # client. Otherwise, break out and accept new connections.

        while True:
            try:
                recv_result, recv_data = recv_bytes(connection, GET_REQUEST_BYTES_SIZE)
                if recv_result and recv_data == GET_REQUEST_BYTES:
                    # Pick a random message (file) and send it to the
                    # client.
                    print("Sending new msg ...")
                    msg = random.choice(Server.MSG_LIST)
                    connection.sendall(msg.encode(MSG_ENCODING))
                    print("Sent message: \n", msg)
                else:
                    # Close the client connection if an invalid
                    # request was made.
                    print("Invalid request or closed connection ... closing ...")
                    connection.close()
                    return
            except socket.error as msg:
                # If the client has closed the connection, close the
                # socket on this end.
                print("Exception: ", msg)
                print("Closing client connection ...")
                connection.close()
                return

########################################################################
# CLIENT
########################################################################

class Client:

    NUMBER_OF_DOWNLOADS = 3    

    RECV_SIZE = 1024
    # RECV_SIZE = 10

    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.download_messages()

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

    def download_messages(self):
        # Download loop to fetch multiple messages from the server.
        for download_number in range(Client.NUMBER_OF_DOWNLOADS):

            # Output some status information.
            print("-" * 72)
            print("Download number: ", download_number+1)

            # Send the download request string to the server.
            self.socket.sendall(GET_REQUEST_BYTES)

            ############################################################
            # Call recv until the entire message is received. Do this
            # by calling recv_bytes.
            ############################################################
            recv_result, recv_data = recv_bytes(self.socket, Server.MSG_SIZE)
            if recv_result:
                print("Message: ", recv_data.decode(MSG_ENCODING))
                print("Done. Closing server connection ... ")
            else:
                print("Recv message failure!")
                self.socket.close()

    def print_msg(self, msg_bytes):
        print("-" * 72)
        print("socket.recv: ", msg_bytes.decode(MSG_ENCODING))

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






