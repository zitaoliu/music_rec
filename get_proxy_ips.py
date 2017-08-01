#!/usr/bin/env python
#coding:utf-8
import sys     
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入     
sys.setdefaultencoding('utf-8')  

import os.path
import subprocess


from bs4 import BeautifulSoup


###
# download good ips 
###
main_file = "ips.html"
test_file = "ip_test_download.html"
good_ip_file = "good_ip_file.txt"

subprocess.call(["wget", "-q", "-O", main_file, "https://free-proxy-list.net/"])
num_cols = 8


###
# read existing good ips
###
ip_dict = set()
with open(good_ip_file) as f:
	for line in f:
		ip_dict.add(line)

print("Have existing good ips: %d \n" %(len(ip_dict)))

good_ips_file = open(good_ip_file, "a")

with open(main_file) as f:
	s = BeautifulSoup(f.read().replace('\n', ''), "html.parser")

	count = 0
	ip_addr = ""
	port_num = ""
	proxy_addr = ""

	for td_item in s.find_all('td'):

		if count % num_cols == 0:
			ip_addr = td_item.string

		if count % num_cols == 1:
			port_num = td_item.string

		if count % num_cols == 2:
			proxy_addr = "http_proxy=" + ip_addr + ":" + port_num

			# if this is the new ip
			if proxy_addr not in ip_dict:

				# test if the ip is working
				return_code = subprocess.call(["wget", "-q", "-T", "3", "-O", test_file, "-e", proxy_addr, "http://music.163.com/playlist?id=574119384"])
	
				if return_code == 0:
					print("Good: " + proxy_addr)
					good_ips_file.write(proxy_addr + "\n")
				else:
					print("Bad: " + proxy_addr)
			
		count = count + 1


good_ips_file.close()