#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import time

# Note: When using telnet to access a web page, you need to "set crlf"
# before connecting.

########################################################################
# Port Forwarding class
########################################################################

class PortForwarder:

    RECV_SIZE = 2048
    BACKLOG = 10

    MSG_ENCODING = "utf-8"

    THIS_HOST = '0.0.0.0'
    LOCAL_PORT  = 50000

    # Map LOCAL_PORT to REMOTE_PORT on localhost.
    REMOTE_HOST = "localhost"
    REMOTE_PORT = 60000

    # Map LOCAL_PORT to REMOTE_PORT on owl.ece.mcmaster.ca
    # REMOTE_HOST = "owl.ece.mcmaster.ca"
    # REMOTE_PORT = 50007 # echo server

    # Map LOCAL_PORT to REMOTE_PORT on owl.ece.mcmaster.ca
    # REMOTE_HOST = "owl.ece.mcmaster.ca"
    # REMOTE_PORT = 80 # Apache web server
    
    def __init__(self):
        self.create_in_socket()
        self.process_connections_forever()

    def create_in_socket(self):
        try:
            # Create an IPv4 TCP listen socket. It will listen on the
            # LOCAL port.
            self.in_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options.
            self.in_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind the input socket to the LOCAL_PORT.
            self.in_socket.bind( (PortForwarder.THIS_HOST, PortForwarder.LOCAL_PORT))

            # Set the (listen) socket to non-blocking mode.
            self.in_socket.setblocking(False)

            # Set socket to listen state.
            self.in_socket.listen(PortForwarder.BACKLOG)
            print("Listening on port {}. ".format(PortForwarder.LOCAL_PORT), end='')
            print("Forwarding to {} at port {} ...".format(PortForwarder.REMOTE_HOST,
                                                           PortForwarder.REMOTE_PORT))

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def create_out_socket(self):
        try:
            # The out socket will connect to whatever is listening on
            # the REMOTE_HOST and REMOTE_PORT.
            self.out_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options.
            self.out_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect to the output host and port.
            self.out_socket.connect((PortForwarder.REMOTE_HOST, PortForwarder.REMOTE_PORT))

            # Set the (listen) socket to non-blocking mode.
            self.out_socket.setblocking(False)

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                try:
                    # Wait for a new client connection to arrive on
                    # the LOCAL_PORT.
                    client = self.in_socket.accept()

                    # Pass the new client connection to the connection
                    # handler.
                    self.connection_handler(client)
                except socket.error:
                    # Do something else while waiting for a
                    # connection. Let's print out a dot every 0.2
                    # seconds.
                    print(".", end="");  sys.stdout.flush()
                    time.sleep(0.2)
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            # self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        client_socket, client_address_port = client

        # We have a new client socket. Set it to non-blocking mode.
        client_socket.setblocking(False)

        print("-" * 72)
        print("Connection received from {}.".format(client_address_port))

        # Create a TCP connection from our out socket to (REMOTE_HOST,
        # REMOTE_PORT).
        self.create_out_socket()

        # Forward data in both directions between the two sockets.
        self.forward_data_between_sockets(client_socket, self.out_socket)

    def forward_data_between_sockets(self, socket_1, socket_2):
        # For proper port forwarding, we need to forward traffic in
        # both directions between the two sockets. To share the same
        # code, we define a socket pair list, then iterate over it and
        # itself in reverse order.
        socket_pair = [socket_1, socket_2]

        while True:
            for r_socket, w_socket in [socket_pair, reversed(socket_pair)]:
                try:
                    # Check for available data on r_socket.
                    recvd_bytes = r_socket.recv(PortForwarder.RECV_SIZE)

                    # Check if the other end of the r_socket has been
                    # closed. If so, close down the two port
                    # forwarding sockets.
                    if len(recvd_bytes) == 0:
                        print()
                        print("Closing connections ...")
                        r_socket.close()
                        w_socket.close()
                        return
                    
                    print("\nReceived: ", recvd_bytes)
                    # Forward any data that has appeared on r_socket
                    # to w_socket.
                    w_socket.sendall(recvd_bytes)
                    print("\nForwarding: ", recvd_bytes)
                except socket.error:
                    # If no bytes are available, process the exception and
                    # do something else while waiting for connection
                    # input. Print out some "!" characters.
                    print("!", end="")
                    sys.stdout.flush()
                    time.sleep(0.1)


########################################################################
# Start up an instance of the port forwarder.
########################################################################

if __name__ == '__main__':
    PortForwarder()

########################################################################






