#!/usr/bin/python3
#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

import os

DEBUG = True
URL = "https://s-jav.com/category/jav-censored-2/?filter=latest"

with requests.get(URL) as page:
    if DEBUG:
        print("requests status_code is {}".format(page.status_code))
    
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.main.find_all("article")

        links = []
        for article in articles:
            page = article.a['href']
            filename = article.a['title'].split('|')[0]
            desc = article.a['title'].split('|')[1]
            
            links.append({
                'page': page,
                'filename': filename,
                'desc': desc,
            })
        
        for link in links:
            with requests.get(link['page']) as link_page:
                temp = BeautifulSoup(link_page.content, "html.parser")
                print(temp)