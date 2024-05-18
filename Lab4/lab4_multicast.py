import socket
import time
import argparse

class Server:

    MULTICAST_ADDRESS = "239.2.2.2"
    MULTICAST_PORT = 2000
    MULTICAST_ADDRESS_PORT = (MULTICAST_ADDRESS, MULTICAST_PORT)
    MSG_ENCODING = "utf-8"

    def __init__(self):
        self.create_send_socket()
        self.send_messages_forever()

    def create_send_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ttl = 1
        ttl_byte = ttl.to_bytes(1, byteorder='big')
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_byte)

    def send_messages_forever(self):
        message_number = 1
        while True:
            message = f"Message {message_number} from server"
            self.socket.sendto(message.encode(self.MSG_ENCODING), self.MULTICAST_ADDRESS_PORT)
            print(f"Sent: {message}")
            time.sleep(2)
            message_number += 1

class Client:

    MULTICAST_ADDRESS = "239.2.2.2"
    MULTICAST_PORT = 2000
    MULTICAST_ADDRESS_PORT = (MULTICAST_ADDRESS, MULTICAST_PORT)
    RECV_SIZE = 256

    def __init__(self):
        self.create_receive_socket()
        self.receive_forever()

    def create_receive_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to 0.0.0.0 (all interfaces) rather than the multicast address
        self.socket.bind(('0.0.0.0', self.MULTICAST_PORT))

        multicast_group_bytes = socket.inet_aton(self.MULTICAST_ADDRESS)
        multicast_iface_bytes = socket.inet_aton("0.0.0.0")
        multicast_request = multicast_group_bytes + multicast_iface_bytes
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)

    def receive_forever(self):
        while True:
            data, _ = self.socket.recvfrom(self.RECV_SIZE)
            print(f"Received: {data.decode('utf-8')}")

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()


