#!/usr/bin/python3
#-*- coding: utf-8 -*-

import requests
import re
import os
from bs4 import BeautifulSoup

TRANSMISSION = "/usr/bin/transmission-remote"
HOST = ""
USERNAME = ""
PASSWORD = ""

#링크 주소
URL = ""
URL_1337 = "https://1337x.to"
HOWMANY = 2

with requests.get(URL) as page:
    list_soup = BeautifulSoup(page.content, "html.parser")

    data_div = list_soup.find("div", {"class" : "table-list-wrap"})
    data_tr= data_div.tbody.find_all("tr")

    links = []
    for tr in data_tr:
        data_item = tr.find_all("a")

        links.append({ 
            "name": data_item[1].string,
            "link": data_item[1].get("href") 
        })

    for link in links[:HOWMANY]:
        with requests.get(URL_1337 + link["link"]) as link_page:
            link_soup = BeautifulSoup(link_page.content, "html.parser")
            link_magnet = link_soup.find("a", href=re.compile("magnet:+"))["href"]

            #os.system ('%s %s --auth %s:%s --add "%s"' % (TRANSMISSION, HOST, USERNAME, PASSWORD, link_magnet))
            command = '%s %s --auth %s:%s --add "%s"' % (TRANSMISSION, HOST, USERNAME, PASSWORD, link_magnet)
            print(command)
