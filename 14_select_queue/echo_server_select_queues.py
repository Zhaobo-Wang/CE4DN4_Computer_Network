#!/usr/bin/env python3

########################################################################

import socket
import argparse
import time
import sys
import base64
import select
import random
import queue

from EchoClientRecvBytes import Client

########################################################################
# SERVER
########################################################################

class Server:

    HOSTNAME = socket.gethostname()
    PORT = 50000

    BACKLOG = 5

    RECV_SIZE = 1024
    # RECV_SIZE = 1

    # Use a zero byte to encode the end of the message. It is not a
    # valid Base64 encoding output.
    EOM_BYTE = b"\0"

    MSG_ENCODING = "utf-8"

    def __init__(self):
        self.create_listen_socket()
        self.initialize_select_lists()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind((Server.HOSTNAME, Server.PORT))
            self.listen_socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            exit()

    def initialize_select_lists(self):
        ################################################################
        # Set the initial lists of read and write sockets that will be
        # passed to the select module. Initially, the read_list will
        # contain only the listen socket that we create. There is
        # nothing to write to yet.
        ################################################################
        self.read_list = [self.listen_socket]
        self.write_list = []

    def process_connections_forever(self):
        ################################################################
        # Define a dictionary of message queues. The dictionary keys
        # will be the sockets associated with the message queues.
        ################################################################
        self.message_queues = {}

        try:
            while True:
                ########################################################
                # Get the current lists of read, write and exception
                # ready sockets from the select module. Select will
                # block until there is something to be done, unless we
                # specify a timeout argument.
                ########################################################
                self.read_ready, self.write_ready, self.except_ready = select.select(
                    self.read_list, self.write_list, [])

                ########################################################
                # There is work to be done. Check both lists that
                # select has returned.
                ########################################################
                self.process_read_sockets()
                self.process_write_sockets()                

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.listen_socket.close()

    def process_read_sockets(self):
        # Iterate through the read ready sockets, processing each one
        # in turn.
        for read_socket in self.read_ready:
            if read_socket is self.listen_socket:
                ########################################################
                # If the read socket is the listen socket, it means
                # that there is a new client connection. Accept it and
                # then append the client socket to the read_list.
                ########################################################
                client, address = read_socket.accept()
                print("-" * 72)
                print("Connection received from {}.".format(address))
                self.read_list.append(client)

                ########################################################
                # Create a new message queue for the new client. Use
                # the client socket as the message_queues dictionary
                # key.
                ########################################################
                self.message_queues[client] = queue.Queue()
            else:
                ########################################################
                # If the read_socket is not the listen socket, then it
                # must be a client socket. Read from the client for
                # input and if it is valid, place it into its
                # associated message queue.
                ########################################################        
                recv_bytes = read_socket.recv(Server.RECV_SIZE)

                if len(recv_bytes):
                    ####################################################
                    # If data came in on the client socket, put the
                    # data into the client message queue.
                    ####################################################
                    self.message_queues[read_socket].put(recv_bytes)

                    ####################################################
                    # Make sure that this socket is on the write_list
                    # so that we can echo the data back to the client.
                    ####################################################
                    if read_socket not in self.write_list:
                        print("Adding read_socket to write_list: ", read_socket)
                        self.write_list.append(read_socket)
                else:
                    ####################################################
                    # If no data was read from the client socket,
                    # therefore the other end has closed. Delete the
                    # message queue for this client, remove the socket
                    # from the read/write lists, then close the socket on
                    # this end.
                    ####################################################
                    print("Closing client connection ... ")
                    print("Deleting message queue ...")
                    del self.message_queues[read_socket]
                    self.read_list.remove(read_socket)
                    if read_socket in self.write_list:
                        self.write_list.remove(read_socket)
                    read_socket.close()

    def process_write_sockets(self):
        ################################################################
        # Iterate through the write ready socket list, processing each
        # one in turn. If there is something there, it is a client
        # waiting for its echo response. Send the top entry in the
        # message queue for that socket.
        ################################################################
        for write_socket in self.write_ready:
            try:
                ########################################################
                # get_nowait will generate a queue.Empty exception if
                # the message queue is empty. When that is the case,
                # remove this socket from the write_list. Otherwise,
                # echo the message. Similarly, if the message queue
                # has been deleted, we will remove the socket from the
                # write_list.
                ########################################################
                next_msg = self.message_queues[write_socket].get_nowait()
                print("sending msg = ", next_msg)
                write_socket.sendall(next_msg)
            except (KeyError, queue.Empty) as msg:
                print(msg)
                print("Removing socket from write_list: ", write_socket)
                self.write_list.remove(write_socket)

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






