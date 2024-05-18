#!/usr/bin/python3

"""
OwlEchoClient class to connect to Owl echo server.

T. D. Todd
McMaster University

"""

########################################################################

import socket
import argparse
import sys

SERVER_HOSTNAME = "compeng4dn4.mooo.com"
SERVER_PORT = 50007

MSG_ENCODING = 'utf-8'

########################################################################
# Echo Client class to connect to compeng4dn4.mooo.com.
########################################################################

class Client:

    # Set the server to connect to. If the server and client are running
    # on the same machine, we can use the current hostname.

    # Try connecting to the compeng4dn4 echo server. You need to change
    # the destination port to 50007 in the connect function below.
    # SERVER_HOSTNAME = 'compeng4dn4.mooo.com'

    RECV_BUFFER_SIZE = 1024 # Used for recv.

    def __init__(self):
        self.getaddrinfodata()
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()

    def getaddrinfodata(self):
        addrinfo_result = socket.getaddrinfo(
            SERVER_HOSTNAME,
            SERVER_PORT,
            family = socket.AF_INET,
            type = socket.SOCK_STREAM,
            proto = socket.IPPROTO_TCP,
            flags = socket.AI_CANONNAME
        )

        # Unpack the result.
        self.addrfamily, self.socktype, self.proto, self.canonname, \
            self.sockaddr = addrinfo_result[0]

        print("\nGetAddrInfo result: ", addrinfo_result, "\n")
        
    def get_socket(self):
        try:

            # Create an IPv4 TCP socket.
            self.socket = socket.socket(self.addrfamily, self.socktype)

            # Allow us to bind to the same port right away.            
            # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind the client socket to a particular address/port.
            # self.socket.bind((Client.HOSTNAME, 40000))
                
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect(self.sockaddr)
            print("Connected to \"{}\" on port {}".format(SERVER_HOSTNAME, SERVER_PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered, i.e., ignore blank lines.
        while True:
            self.input_text = input("Input: ")
            if self.input_text != "":
                break
    
    def send_console_input_forever(self):
        self.connection_receive()                
        while True:
            try:
                self.get_console_input()
                self.connection_send()
                self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                # If we get and error or keyboard interrupt, make sure
                # that we close the socket.
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            self.socket.sendall(self.input_text.encode(MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            print("Received: ", recvd_bytes.decode(MSG_ENCODING))

        except Exception as msg:
            print(msg)
            sys.exit(1)

########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

if __name__ == '__main__':
    Client()

########################################################################

