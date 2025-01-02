from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from nornir_scrapli.tasks import send_command
import os
from rich import print as rprint
import ipdb
from tqdm import tqdm  # simple progress bar
import time
import pathlib # used to create folder/directories to store output files
from datetime import date # used to get current date
nr = InitNornir (config_file="Cisco_Inventory/config.yaml")

# Clearing the Screen
os.system('clear')

# it will be used to stor commands through  user input
show_commands_list = [] 
user_input = input ("Enter commands (type 'Q' or 'Enter' to exit): ")

while user_input:
    show_commands_list.append (user_input)
    user_input = input ("Enter commands (type 'Q' or 'Enter' to exit): ")
    if user_input == "Q" or user_input =="q":
        break
    

'''
this program will archive output of show commands given in file "show_commands_list.txt"
we will archive commands output into hirericaly folder which we will create for each device

User will type command and once he want to finish commands, he will type 'Q' or 'q' 
to terminate loop

We will schdule this task using Cron job, which will execute these commands
every day Moday morning 8:00am and Friday evening 5:00pm
before creating Cron job we need to create bash script which will execute
all commands we type manually to execute this script because Cron schedule Bash script 

make sure bash cript is executeable 
chmod 755 archive_command_output_script.sh

now bash script ready so we can schedule with Crontab job

sudo crontab -e
# -e is used to edit cronttab file

#crontab file configuration for Moday morning 8:00am
0-Sunday, 1-Monday, 2-Tuesday, 3-Wed, 4-Thursday,5-Friday,6-Saturday, 7-Sunday
# m h  dom mon dow   command
0 8 * * 1 cd home/imran/Documents/Automation/Nornir/Runbooks_Repositories/Network_Applications/Archive_Commands_Output && ./archive_command_output_script.sh

#crontab file configuration for Friday evening 5:00pm
0 17 * * 5 cd home/imran/Documents/Automation/Nornir/Runbooks_Repositories/Network_Applications/Archive_Commands_Output && ./archive_command_output_script.sh

Pre-requisite: You have to do intiali cofiguration (IP, OSPF, iBGP) of devices
by executing script "1_Initial_Config.py"

# we can activate cron tab service now
sudo service cron start
'''

def archive_show_commands_output (task, pbar):
    for show_cmd in show_commands_list:
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
    pbar.update () # Update prgress bar once finish All configuration for each device
    
with tqdm (total=len(nr.inventory.hosts), desc = 'Archiving Show commands Output', colour='green') as pbar:
    results = nr.run (task=archive_show_commands_output, pbar=pbar)
print("Archiving of Commands Output Completed !!!\n")
#time.sleep(5) # simulating delay in seconds
print_result (results)
#ipdb.set_trace()


