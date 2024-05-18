#!/usr/bin/env python3

########################################################################
# GET Messages
#
# In this version, the client does multiple "GET"s and does a single
# socket.recv to obtain the response. The server randomly selects from
# a set of message to respond with.
#
# Things may work depending on the client recv size, message length
# and encoding.
#
########################################################################

import socket
import argparse
import time
import sys
import StringSamples
import random

########################################################################

from RecvBytes import *

ENCODING = 'utf-8'
# ENCODING = 'utf-32-le'

GET_REQUEST = 'GET'
GET_REQUEST_SIZE = len(GET_REQUEST) 

GET_REQUEST_BYTES = GET_REQUEST.encode(ENCODING)
# GET_REQUEST_BYTES_SIZE = len(GET_REQUEST_BYTES)

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

    MSG_LIST = [
        "1" * 10,
        "2" * 20,
        "3" * 30,
        "4" * 40,
        "5" * 50,
    ]

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
                recv_result, recv_data = recv_bytes(connection, GET_REQUEST_SIZE)
                # recv_result, recv_data = recv_bytes(connection, GET_REQUEST_BYTES_SIZE)                

                recv_data_decoded = recv_data.decode(ENCODING)
                if recv_result and recv_data_decoded == GET_REQUEST:
                    print("Valid GET received: sending new msg ...")
                    # Pick a random message (file) and send it to the
                    # client.
                    msg = random.choice(Server.MSG_LIST)
                    print("Sending message: \n", msg)
                    connection.sendall(msg.encode(ENCODING))
                    print("Sendall finished.")
                else:
                    # Close the client connection if an invalid
                    # request was made or if the other end closed.
                    print("Invalid request msg or closed connection ... closing ...")
                    connection.close()
                    return
            except socket.error as msg:
                # The socket is ok but has nothing for me.
                print("Socket error receiving GET: ", msg)
                return
            except UnicodeDecodeError as msg:
                print("Unicode decode error: ", msg)
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
            print("Sending GET_REQUEST_BYTES ...")
            self.socket.sendall(GET_REQUEST_BYTES)

            # recvd_bytes is used to accumulate bytes received over the
            # connection.
            recvd_bytes = b""
            
            # In this example, do one recv on the connection and hope
            # for the best.
            try:
                recvd_bytes = self.socket.recv(Client.RECV_SIZE)
                self.print_msg(recvd_bytes)
            except KeyboardInterrupt:
                print()
                sys.exit(1)
        print("Done. Closing server connection ... ")
        self.socket.close()

    def print_msg(self, msg_bytes):
        print("-" * 72)
        print(msg_bytes.decode(ENCODING))

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






