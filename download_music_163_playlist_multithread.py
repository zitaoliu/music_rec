#!/usr/bin/env python
#coding:utf-8
import sys     
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入     
sys.setdefaultencoding('utf-8')  

import json
import numpy as np
import os.path
import re
import subprocess

from multiprocessing import Pool
from bs4 import BeautifulSoup
from selenium import webdriver
from random import randint


music_category_list = ['hot', 'new']

def download_page(url, file_name, ip_set):
	print("[Downloading " + url)
	subprocess.call(["wget", "-q", "-O", file_name, url])


def download_category(music_cat, playlist_cat, offset, file_name, ip_set):
	url = "http://music.163.com/discover/playlist/?order=" + music_cat + "&cat=" + playlist_cat + "&limit=35&offset=" + str(offset)
	print("[Downloading Category] " + url)

	if os.path.exists(file_name):
		return
	
	subprocess.call(["wget", "-q", "-O", file_name, url])
	

def download_playlist(playlist_id, file_name):
	url = "http://music.163.com/playlist?id=" + playlist_id
	print("\t[Downloading Playlist] " + url)

	if os.path.exists(file_name):
		return

	is_ip_good = False
	while len(ip_set) > 0 and ~is_ip_good:
		rand_num = randint(0, len(ip_set))
		ip_proxy = ip_array[rand_num]

		cmd_array = ["wget", "-q", "-T", "5", "-t", "1", "-O", file_name, "-e", ip_proxy, url]
		# print("\t\t" + " ".join(cmd_array))
		return_code = subprocess.call(cmd_array)

		if return_code == 0:
			is_ip_good = True
		else:
			ip_set.remove(ip_proxy)
			print("\t\t" + "[Bad IP removed] " + ip_proxy)

		if len(ip_set) == 0:
			print("No good ip any more")
			quit()

def find_max_page_num(file_name):
	if not os.path.exists(file_name):
		return -1
	else:
		with open(file_name) as f:
			s = BeautifulSoup(f.read().replace('\n', ''), "html.parser")
			val = int(s.find('a', {'class':'zbtn znxt'}).previousSibling.string)
			subprocess.call(["rm", "-rf", file_name])
		return val

def remove_ws(str):
	if str == None:
		return ""
	else:
		return ''.join(str.split())

def like_str_to_num(str):
	if str == None:
		return 0
	else:
		return remove_ws(str)[1:-1]

def extract_num(str):
	if str == None:
		return 0
	else:
		return re.findall('\d+', str)[0]

###
# read existing good ips
###
good_ip_file = "good_ip_file.txt"
ip_set = set()
ip_array = []
with open(good_ip_file) as f:
	for line in f:
		ip_set.add(line)
		ip_array.append(line)

###
# download song category names 
###
main_file = "main.html"
download_category("hot", "%E5%85%A8%E9%83%A8", 0, main_file, ip_set)

song_cat_list = []
song_cat_encoding_list = []

with open(main_file) as f:
	s = BeautifulSoup(f.read().replace('\n', ''), "html.parser")

	for l1_cat_url_tag in s.find_all('dl', {'class':'f-cb'}):
		for l2_cat_url_tag in l1_cat_url_tag.find_all('a', {'class':'s-fc1 '}):
			song_cat_list.append(l2_cat_url_tag['data-cat'])
			items = re.findall(r'(?<=cat=).*?(?=&order)', l2_cat_url_tag['href'])
			song_cat_encoding_list.append(items[0])

###
# download all playlist
###
#
# pool = Pool(processes=4)

for music_cat in music_category_list:
	
	for encoding_idx, encoding_val in enumerate(song_cat_encoding_list):
			
		dir_name = music_cat + "/" + song_cat_list[encoding_idx]
		subprocess.call(["mkdir", "-p", dir_name])

		# download webpage to see the max offset
		tmp_file = dir_name + "/tmp.html"
		tmp_url = "http://music.163.com/discover/playlist/?cat=" + encoding_val + "&order=" + music_cat
		download_page(tmp_url, tmp_file, ip_set)
		num_page = find_max_page_num(tmp_file)
		playlist_offset_list = np.arange(num_page+1) * 35


		for offset in playlist_offset_list:
			print("[" + music_cat + "] [" + song_cat_list[encoding_idx] + ", " + str(encoding_idx) + "/" + str(len(song_cat_encoding_list)) + "], offset = " + str(offset))

			file_name = dir_name + "/" + str(offset) + ".html"
			download_category(music_cat, encoding_val, offset, file_name, ip_set)

			playlist_per_page = []
			with open(file_name) as f:
				s = BeautifulSoup(f.read().replace('\n', ''), "html.parser")

				for playlist in s.find_all('div', {'class':'u-cover u-cover-1'}):

					playlist_name = playlist.a['title']
					playlist_name_rm_ws = remove_ws(playlist_name)
					playlist_id = extract_num(playlist.a['href'])

					visit_count_string = playlist.find('span', {'class':'nb'}).string
					visit_count = int(visit_count_string.replace("万", "0000"))

					playlist_file_name = dir_name + "/" + playlist_id + ".html"
					download_playlist(playlist_id, playlist_file_name)

