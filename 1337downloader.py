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
HOURS = True

DEBUG = False

#토렌트 링크를 얻어오는 함수
def getTorrentsLinks(url):
    checkhours = lambda x: True if x == 'hours' else False #업로드 시간이 시간단위인지 일단위인지 체크하는 람다함수

    with requests.get(URL) as page:
        list_soup = BeautifulSoup(page.content, "html.parser")

        data_div = list_soup.find("div", {"class" : "table-list-wrap"})
        data_tr= data_div.tbody.find_all("tr")

        links = []
        for tr in data_tr:
            data_item = tr.find_all("a")
            data_item_howold = tr.find("td", {"class" : "uploader"}).text.split(' ')  #업로드 시간 체크 목적
            
            links.append({
                "name": data_item[1].string,
                "link": data_item[1].get("href"),
                "howold": (int(data_item_howold[0]), checkhours(data_item_howold[1])),
            })

    return links

#트랜스미션에 토렌트를 추가하는 함수
def addTorrentsLinks(links, host, username, password):
    for link in links:
        with requests.get(URL_1337 + link["link"]) as link_page:
            link_soup = BeautifulSoup(link_page.content, "html.parser")
            link_magnet = link_soup.find("a", href=re.compile("magnet:+"))["href"]

            if DEBUG == True:
                command = '%s %s --auth %s:%s --add "%s"' % (TRANSMISSION, HOST, USERNAME, PASSWORD, link_magnet)
                print(command)
            else: 
                os.system ('%s %s --auth %s:%s --add "%s"' % (TRANSMISSION, HOST, USERNAME, PASSWORD, link_magnet))
            

if __name__ == '__main__':
    links = getTorrentsLinks(URL)
    if HOURS == True:
        temp = []
        for link in links:
            if link["howold"][1] == True:
                temp.append(link)
        links = temp

    addTorrentsLinks(links, HOST, USERNAME, PASSWORD)
