#!/usr/bin/env python3

########################################################################

import socket

########################################################################

# Illustrate how socket.inet_pton, socket.htonl, from_bytes, and to_bytes works.

ipv4_address = "1.2.3.4"
print("ipv4_address = ", ipv4_address)

# inet_pton converts an IPv4 address string in dotted quad
# (presentation) format, to a bytes object in network byte
# (big-endian) order.
ipv4_address_bytes_nbo = socket.inet_pton(socket.AF_INET, ipv4_address)
# print("inet_pton: ", ipv4_address_bytes_nbo)

# Reverse the conversion.
# print("inet_ntop: ", socket.inet_ntop(socket.AF_INET, ipv4_address_bytes_nbo))

# Convert the IP address bytes object back into an int, in
# big-endian byte order.
ipv4_address_int = int.from_bytes(ipv4_address_bytes_nbo, byteorder='big')

# Print it out the way the little-endian machine stores it.
print("Little endian: ", int.to_bytes(ipv4_address_int, length=4, byteorder='little'))
print("Big endian: ", int.to_bytes(ipv4_address_int, length=4, byteorder='big'))


