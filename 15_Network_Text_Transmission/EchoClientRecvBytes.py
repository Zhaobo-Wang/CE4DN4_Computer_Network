#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys

from RecvBytes import *

########################################################################
# Echo Client class
########################################################################

class Client:

    SERVER_HOSTNAME = socket.gethostname()
    RECV_SIZE = 1024
    PORT = 50000

    MSG_ENCODING = 'utf-8'

    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()

    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Client.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.input_text = input("Input: ")
            if self.input_text != '':
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
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            msg = self.input_text.encode(Client.MSG_ENCODING)
            self.msg_length = len(msg)
            self.socket.sendall(msg)
            # print("Sent: ", self.input_text)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            ############################################################
            # Call recv until the entire message is received. Do this
            # by calling recv_bytes.
            ############################################################
            recv_result, recv_data = recv_bytes(self.socket, self.msg_length)
            if recv_result:
                print("Message: ", recv_data.decode(Client.MSG_ENCODING))
            else:
                print("Recv message failure!")
                self.socket.close()
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






