from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
from rich import print as rprint
from tqdm import tqdm  # simple progress bar
import os
import re #regex library
from collections import Counter # used to find duplicate IP addresses
import threading # will be used to write one threat at terminal, Lock, only one thread can write at terminal at same time
from ipaddress import IPv4Address, IPv4Network
#used to valid, manipulate IPV4, in this program we will convert our route/prfix in string form to network and also use it to validate IPv4 address once user type

nr = InitNornir (config_file="Cisco_Inventory/config.yaml")

# Clearing the Screen
os.system('clear')


'''
this program will Search IP addresses in all routing tables of all Cisco IOS devcies
Program will input IP addresses and then will seach in routing table if any routing table
contain route for this ip address

# Provide List of routing table of default VFP, we are intrested to get each prefix/route of
# routing table because we user will provided IP and then we will search if target IP is
# part of this prefix/network that mean this particlar router has route of this IP 
# either directly connected or learned via static or dynamic IP routing
ipdb> pp nr.inventory.hosts['SP-01']['ip_route_info']['vrf']['default']
{'address_family': {'ipv4': {'routes': {'10.1.1.1/32': {'active': True,

# lets unpack above default vrf key further to get our prefixs/routes
# we can iterate these routes and we will get each route of routing table
# but this route is just in form of key, value pair, every key is the unique route of 
#routing table but this key/route is in form of string. we can not treat it as network 
#because this string contain both IP subnets/net mask so to treat it as network and 
#to use this string as network we will use class 'ipaddress' class. 'ipaddress' module help
#us to convert sting into IP addresses and network subnets. 
pdb> pp nr.inventory.hosts['SP-01']['ip_route_info']['vrf']['default']['address_family']['ipv4']['routes']
{'10.1.1.1/32': {'active': True,
                 'metric': 2,
                 'next_hop': {'next_hop_list': {1: {'index': 1,
                                                    'next_hop': '10.1.101.1',
                                                    'outgoing_interface': 'GigabitEthernet0/1',
                                                    'updated': '00:00:06'}}},
                 'route': '10.1.1.1/32',
                 'route_preference': 110,
                 'source_protocol': 'ospf',
                 'source_protocol_codes': 'O'},
 '10.1.101.0/24': {'active': True,
                   'next_hop': {'outgoing_interface': {'GigabitEthernet0/1': {'outgoing_interface': 'GigabitEthernet0/1'}}},
                   'route': '10.1.101.0/24',
                   'source_protocol': 'connected',
                   'source_protocol_codes': 'C'},



# It will provide key, pair vale of IP subnet and IP address with mask, interface could 
have multiple IP subnets so we will iterate over IP subnets key value apirs
ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['GigabitEthernet0/0']['ipv4']
{'172.16.100.2/30': {'ip': '172.16.100.2', 'prefix_length': '30'}}

# it will provide either route is directly connected or learned via OSPF or BGP etc. 
ipdb> pp nr.inventory.hosts['SP-01']['ip_route_info']['vrf']['default']['address_family']['ipv4']['routes']['101.101.101.101/32']
{'active': True,
 'next_hop': {'outgoing_interface': {'Loopback1': {'outgoing_interface': 'Loopback1'}}},
 'route': '101.101.101.101/32',
 'source_protocol': 'connected',
 'source_protocol_codes': 'C'}
ipdb> 
# it will provide outgoing, connected interface incase if network is connected.
ipdb> pp nr.inventory.hosts['SP-01']['ip_route_info']['vrf']['default']['address_family']['ipv4']['routes']['101.101.101.101/32']['
next_hop']['outgoing_interface']
{'Loopback1': {'outgoing_interface': 'Loopback1'}}


ipdb> pp nr.inventory.hosts['SP-01']['ip_route_info']['vrf']['default']['address_family']['ipv4']['routes']['3.3.3.3/32']
{'active': True,
 'metric': 0,
 'next_hop': {'next_hop_list': {1: {'index': 1,
                                    'next_hop': '10.3.1.1',
                                    'updated': '00:40:47'}}},
 'route': '3.3.3.3/32',
 'route_preference': 20,
 'source_protocol': 'bgp',
 'source_protocol_codes': 'B'}

 # if route learned through BGP or OSPF etc, then next_hop_list key will provide 
 # list of all avaible next hopes
 ipdb> pp nr.inventory.hosts['SP-01']['ip_route_info']['vrf']['default']['address_family']['ipv4']['routes']['5.5.5.5/32']['next_hop
']['next_hop_list']
{1: {'index': 1, 'next_hop': '10.5.1.1', 'updated': '01:08:11'}}


'''
#intiate default ipv4 value
ipv4_addr = ""
#if IP address will foun in routing table then we will store IP address, 
# route and device information in this, we will store basically output of print in this list
# because Nornir use multi threading and it crate mess one it print output so instead to print
# we will store output ipv4_addr_list list and at the end we will print the list, 
# if list is empty thats mean ipv4_addr not found
ipv4_addr_list = []

LOCK = threading.Lock ()

def get_ip_route (task, pbar):
    # 'show ip route' will provide routing table of default VRF
    interfaces_result = task.run (task=send_command, command="show ip route")
    task.host['ip_route_info'] = interfaces_result.scrapli_response.genie_parse_output()
    routes = task.host['ip_route_info']['vrf']['default']['address_family']['ipv4']['routes']
    for route in routes:
            net = IPv4Network (route)
            if ipv4_addr in net:
                src_protocol = routes[route]['source_protocol']
                if src_protocol == "connected":
                    try:
                        out_going_interfaces = routes[route]['next_hop']['outgoing_interface']
                        for out_going_interface in out_going_interfaces:
                            exit_intf = out_going_interfaces[out_going_interface]['outgoing_interface']
                            ipv4_addr_list.append (f"{ipv4_addr} is connected to ({ task.host} ) via interface *{exit_intf}* using route ( {net} )")      
                    except KeyError:
                        pass
                else:
                    try:
                        next_hop_list = routes[route]['next_hop']['next_hop_list']
                        for next_hop_index in next_hop_list:
                            next_hop = next_hop_list[next_hop_index]['next_hop']
                            ipv4_addr_list.append (f"{ipv4_addr} is connected to ({ task.host} ) via next hop {next_hop} *{src_protocol}* using route ( {net} )")      
                    except KeyError:
                        pass
                     
    
    pbar.update () # Update prgress bar once finish All configuration for each device

while True:
    ipv4_addr = input ("Enter IPv4 Address in format (or 'quit' to stop):- ")
    if ipv4_addr.lower() == 'quit':
        ipv4_addr = ""
        break
    else:
        try:
            # it will convert normal IPv4 string to IPv4 if input is not valid IPv4 generate valueError
            ipv4_addr = IPv4Address (ipv4_addr)
            break
        except ValueError:
            print (f"its not valid IPv4 address {ipv4_addr}")
            ipv4_addr = ""


with tqdm (total=len(nr.inventory.hosts), desc = 'Gathering IP Route Details', colour='green') as pbar:
        results = nr.run (task=get_ip_route, pbar=pbar)

if ipv4_addr_list:
    ipv4_addr_list.sort ()
    for ipv4_list_element in ipv4_addr_list:
        rprint (ipv4_list_element)
else:
     rprint (f"{ipv4_addr} not found in routing table of any device !!!")
#import ipdb
#ipdb.set_trace()


