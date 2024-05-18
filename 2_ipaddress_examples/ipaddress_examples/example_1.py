#!/usr/bin/python

from common import *
import ipaddress

######################################################

my_ipv4_address = ipaddress.ip_address('192.168.0.1')
# my_ipv4_address = ipaddress.ip_address('1.0.0.2')

output_line()
print("my_ipv4_address = ", my_ipv4_address)
output_line()

# or, you can force an IPv4 or IPv6 address:
# print(ipaddress.IPv4Address('192.168.0.1'))

print("type(my_ipv4_address) = ", type(my_ipv4_address))

# dir(object). List the names (attributes) defined in the given object, i.e.,
# functions, classes and variables.
#print("dir(my_ipv4_address) = ", dir(my_ipv4_address))

# Output object as a string.
# print("str(my_ipv4_address) = ", str(my_ipv4_address))
# print("my_ipv4_address.__str__() = ", my_ipv4_address.__str__())

# Test the type of IP address.
# print("my_ipv4_address.is_loopback = ", my_ipv4_address.is_loopback)
# print("my_ipv4_address.is_global = ", my_ipv4_address.is_global)
# print("my_ipv4_address.is_private = ", my_ipv4_address.is_private)

# Get printable representation of an object. Tries to give a string
# that would give the same result if run by eval().
# print("repr(my_ipv4_address) = ", repr(my_ipv4_address))
# print("my_ipv4_address.__repr__() = ", my_ipv4_address.__repr__())
# print("type(my_ipv4_address.__repr__()) = ", type(my_ipv4_address.__repr__()))

# Get the IP address in different string formats.
# print("int(my_ipv4_address) = ", int(my_ipv4_address))
# print("bin(int(my_ipv4_address)) = ", bin(int(my_ipv4_address))) # creates a string
# print("hex(int(my_ipv4_address)) = ", hex(int(my_ipv4_address))) # creates a string

# Do some simple math with IP addresses.
for n in range(1, 10):
    print(ipaddress.ip_address("192.168.1.250") + n)

# Create IP address directly from bytes objects.
my_address_bytes = b'\xc0\xa8\x00\x01'
print(my_address_bytes)
# print("ipaddress.ip_address(my_address_bytes) = ", ipaddress.ip_address(my_address_bytes))

# Created directly from integer objects.
# my_address_int = 3232235521
# print(my_address_int)
# print("ipaddress.ip_address(my_address_int) = ", ipaddress.ip_address(my_address_int))

