from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_configs
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.data import load_yaml
import os
from rich import print
from tqdm import tqdm  # simple progress bar
import time


nr = InitNornir (config_file="Inventory/config.yaml")

# Clearing the Screen
os.system('clear')

'''
this program will Configure IP addesses, OSPF and eBGP as base configuration for IOs & Arista

Prerequisite: VAR Files and J2 templates 

Variable Files: load variable from VARS(variable files), VARS are define for each host

Pre-requisite: NA
'''

def config_device_ip_j2_template(task):
    ip_cfg_template = task.run (task=template_file, template=f"config_dev_ip.j2", path=f"J2_Templates/{task.host.platform}")
    task.host['dev_ip_cfg'] = ip_cfg_template.result
    dev_ip_cfg_rendered = task.host['dev_ip_cfg']
    dev_ip_config = dev_ip_cfg_rendered.splitlines()
    task.run (task=send_configs, configs=dev_ip_config)

def config_ospf_j2_template(task):
    ospf_cfg_template = task.run (task=template_file, template=f"config_dev_ospf.j2", path=f"J2_Templates/{task.host.platform}")
    task.host['dev_ospf_cfg'] = ospf_cfg_template.result
    dev_ospf_cfg_rendered = task.host['dev_ospf_cfg']
    dev_ospf_config = dev_ospf_cfg_rendered.splitlines()
    task.run (task=send_configs, configs=dev_ospf_config)

def config_eBGP_j2_template(task):
    eBGP_cfg_template = task.run (task=template_file, template=f"bgp.j2", path=f"J2_Templates/{task.host.platform}")
    task.host['dev_bgp_cfg'] = eBGP_cfg_template.result
    dev_bgp_cfg_rendered = task.host['dev_bgp_cfg']
    dev_bgp_config = dev_bgp_cfg_rendered.splitlines()
    task.run (task=send_configs, configs=dev_bgp_config)

def config_ip_ebgp_vars_j2_template (task, pbar):
    
    try:
        # First of all we need to load variables (vars) for hosts using load_yaml, 
        # it will return yaml data in dictionary form
        dev_data = task.run (task=load_yaml, file=f"./Hosts_VARS/{task.host.platform}/{task.host}.yaml")
        task.host['dev_vars'] = dev_data.result
    except:
        print (f'*** An error occured during Loading Hosts_Variables at {task.host} ***')
    try:
        #Now vars are loaded, Lets configure Devices, in our lab we will configuration 
        # IP addresses configuration using j2 template
        config_device_ip_j2_template(task)
    except:
        print (f'*** An error occured during IP Configuration on Interfaces at {task.host} ***')
    
    try:
        # eBGP/iBGP using loo0 as source required TCP/IP reachability to neighbors so we need to configure any IGP
        # OSPF configurations using j2 template for iBGP/eBGP peer reachability
        config_ospf_j2_template(task)
    except:
        print (f'*** An error occured during OSPF Configuration at {task.host} ***')
    
    try:
        # iBGP configuration using j2 template
        config_eBGP_j2_template(task)
    except:
        print (f'*** An error occured during eBGP Configuration at {task.host} ***')
    
    pbar.update () # Update prgress bar once finish All configuration for each device

# we are creating progress bar for total devices we have in our inventory
# tqdm is used to create simple progress bar
with tqdm (total=len(nr.inventory.hosts), desc = 'Configuring Devices', colour='green') as pbar:
    results = nr.run (task=config_ip_ebgp_vars_j2_template, pbar=pbar)
    #print_result (results)
print("Configuration Completed !!!\n")
#time.sleep(5) # simulating delay in seconds
#print_result (results)
#import ipdb
#ipdb.set_trace()


