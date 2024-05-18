#!/usr/bin/env python3

########################################################################
# GET Messages
#
# In this version, the server appends a special character to the end
# of the transmitted message. The client uses this to know that the
# message transmission is complete. Care must be taken to ensure that
# the special character cannot appear in the message payload. To
# accomplish this, Base64 encoding is used.
#
########################################################################

import socket
import argparse
import time
import sys
import StringSamples
import random
import struct
import base64
import binascii

from RecvBytes import *

GET_REQUEST = b'GET'
GET_REQUEST_SIZE = len(GET_REQUEST)

########################################################################
# SERVER
########################################################################

class Server:

    HOSTNAME = socket.gethostname()
    PORT = 50000

    RECV_SIZE = 100

    BACKLOG = 5

    SIZE_FIELD_LENGTH = 4 # number of bytes

    # Define a list of messages. When a client sends a "GET", select
    # one randomly and return it.

    MSG_LIST = [
        "1" * 72,
        "2" * 72,
        "3" * 72,
        "4" * 72,
        "5" * 72,
    ]

    ####################################################################
    # Use a zero byte to signal the end of the message. It is not a
    # valid Base64 encoding output.
    ####################################################################    

    EOM_BYTE = b"\0"

    MSG_ENCODING = "utf-8"

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
            print(msg); exit()

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
                if recv_result and recv_data == GET_REQUEST:
                    print("Received GET ...")
                    # Pick a random message (file) and send it to the
                    # client.
                    msg = random.choice(Server.MSG_LIST)
                    print("Sending message: \n", msg)
                    msg_encoded = msg.encode(Server.MSG_ENCODING)
                    ####################################################
                    # Do a Base64 encoding of the message so that it
                    # is transferred using a subset of ASCII
                    # characters. Append the EOM_BYTE to the end of
                    # the message so that the client can test for the
                    # end-of-message.
                    ####################################################
                    msg_base64 = base64.b64encode(msg_encoded)
                    msg_total = msg_base64 + Server.EOM_BYTE
                    print("Sending base64 message bytes + EOM_BYTE: \n", msg_total)
                    # print("Sending base64 (hex) message bytes: \n", binascii.hexlify(msg_total))
                    connection.sendall(msg_total)
                else:
                    # Close the client connection if an invalid
                    # request was made.
                    print("Closing client connection ...")
                    connection.close()
                    return
            except socket.error:
                # If the client has closed the connection, close the
                # socket on this end.
                print("Closing client connection ...")
                connection.close()
                return

########################################################################
# CLIENT
########################################################################

class Client:

    RECV_SIZE = 10
    NUMBER_OF_DOWNLOADS = 2

    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.download_messages()

    def get_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg); exit()

    def connect_to_server(self):
        try:
            self.socket.connect((Server.HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg); exit()

    def download_messages(self):

        # Download loop to fetch multiple messages from the server.
        for download_number in range(1, Client.NUMBER_OF_DOWNLOADS+1):

            # Output some status information.
            print("-" * 72)
            print("Download number: ", download_number)

            # Send the download request string to the server.
            self.socket.sendall(GET_REQUEST)

            # recvd_pkt_bytes is used to accumulate bytes received over
            # the connection.
            recvd_bytes_total = bytearray()

            # Use the msg size field to read from the socket until all
            # bytes are received.
            try:
                while True:
                    recvd_bytes_total += self.socket.recv(Client.RECV_SIZE)
                    ####################################################
                    # Check if the current end of the received bytes
                    # consists of the EOM_BYTE character. If so, we
                    # are done.
                    ####################################################                    
                    if recvd_bytes_total[-1:] == Server.EOM_BYTE:
                        ################################################
                        # Remove the EOM_BYTE from the message bytes.
                        ################################################                        
                        recvd_msg_bytes = recvd_bytes_total[:-1]

                        # Decode the message and print it out.
                        msg = base64.b64decode(recvd_msg_bytes).decode(Server.MSG_ENCODING)
                        print(msg)
                        break
            except KeyboardInterrupt:
                print()
                sys.exit(1)
            # If the socket has been closed by the server, break out
            # and close it on this end.
            except socket.error:
                break
        print("Closing server connection ... ")
        self.socket.close()

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






