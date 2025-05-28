from nornir_utils.plugins.functions import print_result
from collections import Counter

ip_list = [ '1.0.1.1', '1.1.1.1', '2.2.2.2.2', '3.3.3.3', '1.1.1.1', '2.2.2.2.2', '1.1.1.1', '3.3.3.3', '3.3.3.3', '5.5.5.5' ]

count_ip_list = Counter(ip_list)
for k, v in count_ip_list.items ():
    # if value of count is more than one thats me IP is duplicate
    if v > 1:
        print (f"IP addrss {k} duplicated {v} times")

#print (count_ip_list['2.2.2.2.2'])
#print (count_ip_list['7.7.7.7'])
#print (count_ip_list['3.3.3.3'])

#we can achive same above result using list comprehension 
list_comprehension = [k for k, v in Counter(count_ip_list).items () if v > 1]
print (list_comprehension)