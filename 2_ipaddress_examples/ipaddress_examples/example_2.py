#!/usr/bin/python

from common import *
import ipaddress

######################################################
# IP Network objects (The host bits must all be zero).
######################################################

my_ipv4_network = ipaddress.ip_network('192.168.1.0/24') # Class C netmask.
# my_ipv4_network = ipaddress.ip_network('130.113.0.0/16') # Class B netmask.

output_line()
print("my_ipv4_network = ", my_ipv4_network)
output_line()

# print("type(my_ipv4_network) = ", type(my_ipv4_network))
print("my_ipv4_network.num_addresses = ", my_ipv4_network.num_addresses)
print("my_ipv4_network.netmask = ", my_ipv4_network.netmask)
print("bin(int(my_ipv4_network.netmask)) = ", bin(int(my_ipv4_network.netmask)))
# print("my_ipv4_network.is_private = ", my_ipv4_network.is_private)
# also .is_global, .is_multicast.
# print("my_ipv4_network.broadcast_address = ", my_ipv4_network.broadcast_address)

# print("my_ipv4_network.with_netmask = ", my_ipv4_network.with_netmask)
# print("my_ipv4_network.with_prefixlen = ", my_ipv4_network.with_prefixlen)
# print("type(my_ipv4_network.with_prefixlen) = ", type(my_ipv4_network.with_prefixlen))

# output_line()

# Iterate over some defined subnets.

for net in my_ipv4_network.subnets(prefixlen_diff=4): # extend subnet by 4 bits
    print(net, "(num_addresses = {})".format(net.num_addresses))


# output_line()

'''
for net in my_ipv4_network.subnets(new_prefix=26): # extend subnet by 2 bits
    print(net, "(num_addresses = {})".format(net.num_addresses))    
    print(bin(int(net.network_address)))    
    print(bin(int(net.netmask)))
'''

# Create a list of the subnets formed above.
# Note "subnets()" creates a generator.
# print(list(my_ipv4_network.subnets(new_prefix=26)))

# We can use .hosts() as a list of address objects in the network
# (remove un-assignable addresses)
'''
my_ipv4_subnet = ipaddress.ip_network('192.168.1.0/29')
for h in my_ipv4_subnet.hosts():
    print(h)
'''

# We can also index the network addresses inside a network.
'''
print("my_ipv4_network[0] = ", my_ipv4_network[0])
print("my_ipv4_network[1] = ", my_ipv4_network[1])
print("my_ipv4_network[2] = ", my_ipv4_network[2])
print("list(my_ipv4_network)[0:8] = ", list(my_ipv4_network)[0:8])
'''

# Is HOST in a network?
'''
HOST_LIST = ['10.0.30.1', '10.0.40.1']

NETWORK = '10.0.0.0/255.255.224.0'
my_network = ipaddress.ip_network(NETWORK)

for host in HOST_LIST:
    if ipaddress.ip_address(host) in my_network:
        print("Host {} is in {}".format(host, NETWORK))
    else:
        print("Host {} is not in {}".format(host, NETWORK))
'''


