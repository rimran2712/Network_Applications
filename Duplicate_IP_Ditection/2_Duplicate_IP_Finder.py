from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
from rich import print as rprint
from tqdm import tqdm  # simple progress bar
import os
import re #regex library
from collections import Counter # used to find duplicate IP addresses
import threading # will be used to write one threat at terminal, Lock, only one thread can write at terminal at same time
nr = InitNornir (config_file="Cisco_Inventory/config.yaml")

# Clearing the Screen
os.system('clear')


'''
this program will find the Duplicate IPv4 address from the whole network topology
If it will find IPv4 confilict, It will provide information about devices, interface
where IP found.

# Provide List of Interfaces, we can Itirate it
ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']

# It will provide key, pair vale of IP subnet and IP address with mask, interface could 
have multiple IP subnets so we will iterate over IP subnets key value apirs
ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['GigabitEthernet0/0']['ipv4']
{'172.16.100.2/30': {'ip': '172.16.100.2', 'prefix_length': '30'}}

#provide exact IP address
ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['GigabitEthernet0/0']['ipv4']['172.16.100.2/30']['ip']
'172.16.100.2'

# This interface does not have any IP address so will genrate Key error
ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['GigabitEthernet0/3']['ipv4']
*** KeyError: 'ipv4'

ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['Loopback5']['ipv4']
*** KeyError: 'Loopback5'

# provide chassis Serial Number
ipdb> pp nr.inventory.hosts['vIOS-R8']['version_info']['version']['chassis_sn']
'9TZ9VMOEFONM558O6AE48'

'''

ip_addr_list = []
#intiate list to store all IP addresses

duplicate_ip_list = []
#intiate list to store duplicate IP addresses only which we found from above list

LOCK = threading.Lock

def get_ip_addresses (task, pbar):
    interfaces_result = task.run (task=send_command, command="show ip interface")
    task.host['interfaces_info'] = interfaces_result.scrapli_response.genie_parse_output()
    interfaces_data = task.host['interfaces_info']
    for interface in interfaces_data:
        try:
            ip_subnet_key = interfaces_data[interface]['ipv4']
            for ip in ip_subnet_key: #Iterate at IP_subnet_key to get primary and secondary IP of interface
                ip_addr = ip_subnet_key[ip]['ip']
                # append all the ip addresses into list and later we can analize list 
                # and find duplicate IP addresses in list usinf counter object in collection library
                ip_addr_list.append (ip_addr) 
                #rprint (f"[bold green]{task.host}'s {interface} has IP Address [ {ip_addr} ][/bold green]")
        except KeyError:  # Skip the interfaces who does not have IP addresses assigned
            pass
    pbar.update () # Update prgress bar once finish All configuration for each device


def find_duplicate_ip_address (task):
    dup_interfaces_result = task.run (task=send_command, command="show ip interface")
    task.host['dup_interfaces_info'] = dup_interfaces_result.scrapli_response.genie_parse_output()
    dup_interfaces_data = task.host['dup_interfaces_info']
    for interface in dup_interfaces_data:
        try:
            ip_subnets_key = dup_interfaces_data[interface]['ipv4']
            for ip in ip_subnets_key: #Iterate at IP_subnet_key to get primary and secondary IP of interface
                ip_addr = ip_subnets_key[ip]['ip']
                if ip_addr in duplicate_ip_list:
                    # if duplicate IP found then we need to gather device version information
                    version_result = task.run (task=send_command, command="show version")
                    task.host['version_info'] = version_result.scrapli_response.genie_parse_output()
                    serial_number = task.host['version_info']['version']['chassis_sn']
                    rprint (f"[bold green]{task.host} SN#({serial_number}) {interface} has Duplicate IP Address [ {ip_addr} ][/bold green]")
        except KeyError:  # Skip the interfaces who does not have IP addresses assigned
            pass

#time.sleep(5) # simulating delay in seconds
#print_result (results)

with tqdm (total=len(nr.inventory.hosts), desc = 'Gathering IP Addresses', colour='green') as pbar:
        results = nr.run (task=get_ip_addresses, pbar=pbar)

ip_list_dict = Counter(ip_addr_list)
for k, v in ip_list_dict.items ():
    # k is "ip address" & v is occurance ip ip address
    # if value (v) is more than one thats me IP is duplicate
    if v > 1:
        # store duplicate IP in duplicate list
        duplicate_ip_list.append (k) 

# If Duplicate IP addresses exist in list, need to get more details
if duplicate_ip_list:
        rprint (f"\n[bold red]Duplicate IP Found[/bold red]")
        nr.run (task=find_duplicate_ip_address)
else:
    rprint (f"\n[bold green]No Duplicate IP Found !!!![/bold green]")
#import ipdb
#ipdb.set_trace()


