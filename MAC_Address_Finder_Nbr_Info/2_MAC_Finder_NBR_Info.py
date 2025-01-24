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

'''

mac_input = ""

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
        rprint (f"[bold red]\nInvalid MAC Addrees: [ {mac_input.lower()} ][/bold red]")


def mac_address_finding (task, pbar):
    interfaces_result = task.run (task=send_command, command="show interfaces")
    task.host['interfaces_info'] = interfaces_result.scrapli_response.genie_parse_output()
    interfaces_data = task.host['interfaces_info']
    for interface in interfaces_data:
        mac_address = interfaces_data[interface]['mac_address']
        if mac_address == mac_input.lower():
            rprint (f"[bold green]{task.host}'s {interface} has MAC Address [ {mac_input.lower()} ][/bold green]")
        #else:
        #    rprint (f"[bold red]\nMAC Addrees Not Found: [ {mac_input.lower()} ][/bold red]")



    
    '''
    # Open the file in read mode
    with open("show_commands_list.txt") as show_commands_file:
        # Read each line one by one
        for show_cmd in show_commands_file:
            # if users does not type any command or line is empty than we dont need to send command
            if show_cmd != "\n" or show_cmd == "": 
                try:
                    output_file_name = show_cmd.replace (' ', '_')
                    # main folder where we will store all commands output under subfolders
                    output_folder_name = "Commands_Output"
                    # Date name folder inside main output folder
                    date_folder = output_folder_name + "/" + str (date.today())
                    # Hostname folder inside main date name folder
                    device_folder = date_folder + "/" + f"{task.host}"
                    pathlib.Path(output_folder_name).mkdir(exist_ok=True) # exist_ok True mean if folder already exist than dont over write, done create
                    pathlib.Path(date_folder).mkdir(exist_ok=True) # create sub folder - date folder
                    pathlib.Path(device_folder).mkdir(exist_ok=True) # create sub folder for each host
                    
                    # Send Command and store result in output variable
                    output = task.run (task=send_command, command=show_cmd)
                    # output.result attribute storer value of output

                    # Lets write the output of command into file
                    task.run (
                        task=write_file,
                        content=output.result,
                        filename= str (device_folder + "/" + output_file_name)

                    )
                except:
                    print ("Invalid Command Dettected: ", show_cmd)
    '''
    pbar.update () # Update prgress bar once finish All configuration for each device

if mac_input != "":
    with tqdm (total=len(nr.inventory.hosts), desc = 'MAC Address Finding', colour='green') as pbar:
        results = nr.run (task=mac_address_finding, pbar=pbar)

print("MAC Search Completed !!!\n")
#time.sleep(5) # simulating delay in seconds
#print_result (results)
#import ipdb
#ipdb.set_trace()

