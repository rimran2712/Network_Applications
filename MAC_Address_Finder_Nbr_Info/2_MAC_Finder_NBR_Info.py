from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
from rich import print as rprint
from tqdm import tqdm  # simple progress bar
import os
import re #regex library

nr = InitNornir (config_file="Cisco_Inventory/config.yaml")

# Clearing the Screen
os.system('clear')


'''
this program will find the MAC address from the whole network topology
If MAC found than it will get information of its connected neighbor on the interace
having MAC address.

user will input valid MAC address in Cisco MAc address format

# MAC Addess validation regex
# pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'


pdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']
{'GigabitEthernet0/0': {'arp_timeout': '04:00:00',
                        'arp_type': 'arpa',
                        'bandwidth': 1000000,
.....
.....
.....

ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['GigabitEthernet0/1']['mac_address']
'5057.5700.0a01'

ipdb> pp nr.inventory.hosts['vIOS-R1']['interfaces_info']['Loopback0']['mac_address']
*** KeyError: 'mac_address'

ipdb> pp nr.inventory.hosts['vIOS-R1']['cdp_info']['cdp']['index']
{1: {'capability': 'R S I',
     'device_id': 'MGMT-vSW',
     'hold_time': 141,
     'local_interface': 'GigabitEthernet0/0',
     'platform': '',
     'port_id': 'GigabitEthernet0/0'},
 2: {'capability': 'R B',
     'device_id': 'vIOS-R6.mylab.local',
     'hold_time': 172,
     'local_interface': 'GigabitEthernet0/2',
     'platform': 'Gig',
     'port_id': '0/2'},
 3: {'capability': 'R B',
     'device_id': 'vIOS-R5.mylab.local',
     'hold_time': 147,
     'local_interface': 'GigabitEthernet0/1',
     'platform': 'Gig',
     'port_id': '0/1'}}
ipdb> 


'''

mac_input = ""
#intiate default mac value
mac_found = False
#intiate default mac status

while True:
    mac_input = input ("Enter MAC Address in format [50ed.d800.ab100] (or 'quit' to stop):- ")
    if mac_input.lower() == 'quit':
        mac_input = ""
        break
    #elif re.match (r"[0-9a-f]{4}([.:-]?)[0-9a-f]{4}\1[0-9a-f]{4}$", mac_input.lower()):
    elif re.match (r"[0-9a-f]{4}([.]?)[0-9a-f]{4}\1[0-9a-f]{4}$", mac_input.lower()):
        #rprint (f"[bold green]You Enter Correct MAC Address: [ {mac_input.lower()} ][/bold green]")
        break
    else:
        rprint (f"[bold red]\nInvalid MAC Addrees: [ {mac_input.lower()} ][/bold red]\n")


def mac_address_finding (task, pbar):
    interfaces_result = task.run (task=send_command, command="show interfaces")
    task.host['interfaces_info'] = interfaces_result.scrapli_response.genie_parse_output()
    interfaces_data = task.host['interfaces_info']
    for interface in interfaces_data:
        try:
            mac_address = interfaces_data[interface]['mac_address']
            if mac_address == mac_input.lower():
                global mac_found
                mac_found = True
                rprint (f"[bold green]{task.host}'s {interface} has MAC Address [ {mac_input.lower()} ][/bold green]")
                rprint (f"[cyan]Generating Neighbor Details....[/cyan]")
                nbr_info (task, interface)
                break
        except KeyError:  # Loopback does not have MAC addess key so we need to skip loopback
            pass
    
    pbar.update () # Update prgress bar once finish All configuration for each device

def nbr_info (task, interface):
    nbr_found = False
    cdp_result = task.run (task=send_command, command="show cdp neighbors")
    task.host['cdp_info'] = cdp_result.scrapli_response.genie_parse_output()
    nbr_index = task.host['cdp_info']['cdp']['index']
    for nbr in nbr_index:
        if interface == nbr_index[nbr]['local_interface']: #find intrested local interface
            nbr_found = True
            remote_dev = nbr_index[nbr]['device_id']
            remote_intferface = nbr_index[nbr]['port_id']
            remote_platform = nbr_index[nbr]['platform']
            rprint (f"[bold green]{interface} Connected to {remote_dev}'s Interface {remote_platform} {remote_intferface} [/bold green]")
    if nbr_found != True:
        rprint (f"[bold red]{interface} is not connected with any device or Interface down[/bold red]")
if mac_input != "":
    rprint (f"[bold green]Searching for the MAC Address [ {mac_input} ][/bold green]")
    with tqdm (total=len(nr.inventory.hosts), desc = 'MAC Address Finding', colour='green') as pbar:
        results = nr.run (task=mac_address_finding, pbar=pbar)
#        print_result (results)

if mac_found == False  and mac_input != "":
    rprint (f"\n[bold red]MAC address not found[/bold red]")

rprint (f"\n[green]Goodbye !!!\n[/green]")
#time.sleep(5) # simulating delay in seconds
#print_result (results)
#import ipdb
#ipdb.set_trace()

