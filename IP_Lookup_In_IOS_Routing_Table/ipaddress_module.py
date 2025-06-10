from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
from rich import print as rprint
from tqdm import tqdm  # simple progress bar
import os
import re #regex library
from collections import Counter # used to find duplicate IP addresses
import threading # will be used to write one threat at terminal, Lock, only one thread can write at terminal at same time
from ipaddress import ip_address, IPv4Address, IPv4Network, ip_network
#used to valid, manipulate IPV4/IPV6, in this program we will convert our route/prfix in string form to network and also use it to validate IPv4 address once user type


"""
get_IPv4_orIPv6 = input ("enter Valid IPv4 or IPv6: ")

# it will convert normal IPv4 or IPv6 string to IPv4 or IPv6 if input if valid IPv4 or IPv6
# otherwise will generate valueError
try:
    IPv4_orIPv6 = ip_address (get_IPv4_orIPv6)
    print (f"its valid IPv4 or IPv6 address {IPv4_orIPv6}")
except ValueError:
    print (f"its not valid IPv4 or IPv6 address {get_IPv4_orIPv6}")

get_IPv4 = input ("Enter Valid IPv4: ")

# it will convert normal IPv4 string to IPv4 if input is not valid IPv4 generate valueError
try:
    IPv4 = IPv4Address (get_IPv4)
    print (f"its valid IPv4 address {IPv4}")
except ValueError:
    print (f"its not valid IPv4 address {get_IPv4}")

ipv4_prefix_list = ["10.0.0.0/8", "172.160.0.0/16", "192.168.1.0/25", "2001::1/64"]

for ipv4_prefix in ipv4_prefix_list:
    try:
        # convert every prixy string to ipv4 network to treat in code as network
        ipv4_route = IPv4Network (ipv4_prefix)
        if IPv4 in ipv4_route:
            print (f"{IPv4} is part of network {ipv4_route}")
    except ValueError:
        print (f"its not valid IPv4 Prifix {ipv4_prefix}")

"""

#intiate default ipv4 value
ipv4_addr = ""

while True:
    ipv4_addr = input ("Enter IPv4 Address in format (or 'quit' to stop):- ")
    if ipv4_addr.lower() == 'quit':
        ipv4_addr = ""
        break
    else:
        try:
            # it will convert normal IPv4 string to IPv4 if input is not valid IPv4 generate valueError
            ipv4_addr = IPv4Address (ipv4_addr)
            print (f"its valid IPv4 address {ipv4_addr}")
            break
        except ValueError:
            print (f"its not valid IPv4 address {ipv4_addr}")


#import ipdb
#ipdb.set_trace()


