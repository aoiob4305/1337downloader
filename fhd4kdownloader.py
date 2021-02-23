#!/usr/bin/python3
#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

import os

DEBUG = True
URL = "http://fhd4k.com/forum-2-1.html"
URL_PRE = "http://fhd4k.com/"

TRANSMISSION = "/usr/bin/transmission-remote"
HOST = "192.168.12.16"
USERNAME = "admin"
PASSWORD = "!kim9119"

with requests.get(URL) as page:
    if DEBUG:
        print("requests status_code is {}".format(page.status_code))
    
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        lists = soup.find_all("td", {"class": "icn"})[1:]
        
        links = []
        for link in lists:
            link_url = URL_PRE + link.a["href"]
            if DEBUG: print(link_url)
            
            with requests.get(link_url) as link_page:
                if link_page.status_code == 200:
                    link_soup = BeautifulSoup(link_page.content, "html.parser")
                    link_magnet = link_soup.find("div", {"class": "blockcode"}).li.text

                    if DEBUG: print(link_magnet)
                    links.append(link_magnet)

                    if DEBUG:
                        print('%s %s --auth %s:%s --add "%s"' % (TRANSMISSION, HOST, USERNAME, PASSWORD, link_magnet))
                    else:
                        os.system('%s %s --auth %s:%s --add "%s"' % (TRANSMISSION, HOST, USERNAME, PASSWORD, link_magnet))
    else:
        print("requests was failed")