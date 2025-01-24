import re

# MAC Addess validation regex
# pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

cmd_input = ""

while True:
    cmd_input = input ("Enter MAC Address in format [50ed.d800.ab100] (or 'quit' to stop):- ")
    if cmd_input.lower() == 'quit':
        cmd_input = ""
        break
    elif re.match (r"[0-9a-f]{4}([.:-]?)[0-9a-f]{4}\1[0-9a-f]{4}$", cmd_input.lower()):
        print (f"You Enter Correct MAC Address: [ {cmd_input.lower()} ]")
        break
    else:
        print (f"\nInvalid MAC Addrees: [ {cmd_input.lower()} ]")

