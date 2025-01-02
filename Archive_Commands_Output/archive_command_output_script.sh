#!/bin/bash

# activate virtual enviorment where we will run python script
source /home/imran/Documents/Automation/Nornir/.MyNAPALMvenv/bin/activate
#change directory to script location
cd /home/imran/Documents/Automation/Nornir/Runbooks_Repositories/Network_Applications/Archive_Commands_Output
# run script to archivethe Output of commands
python3 2_Archive_Output_commands_from_file.py 

# De-activate virtual enviorment 
sudo service cron start