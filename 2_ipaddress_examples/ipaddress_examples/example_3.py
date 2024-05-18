#!/usr/bin/python

from common import *
import ipaddress

######################################################
# IP interface objects.
######################################################

# Is a subclass of IP address object, so it inherits all the
# attributes from that class. It uses the same constructor format
# except that arbitrary host bits can be set.

interface = ipaddress.IPv4Interface('192.168.1.22/24')
print("interface = ", interface)
output_line()

print("interface.ip = ", interface.ip)
print("interface.network = ", interface.network)
print("interface.with_prefixlen = ", interface.with_prefixlen)
print("interface.with_netmask = ", interface.with_netmask)

