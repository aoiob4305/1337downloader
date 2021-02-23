#!/usr/bin/python3
#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

import os

DEBUG = True
URL = "https://www.ebooksyard.com/"

def download(url, filename):
    if os.path.isfile(filename) == False:    
        with open(filename, "wb") as file:   # open in binary mode
            response = requests.get(url)               # get request
            file.write(response.content)      # write to file
    else:
        if DEBUG:
            print("file is exist")

with requests.get(URL) as page:
    if DEBUG:
        print("requests status_code is {}".format(page.status_code))
    
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        elementors = soup.find_all("div", {"class":"elementor-row"})

        posts = elementors[0].find_all("div", {"class":"pgafu-post-grid-content"})
        for post in posts[0:2]:
            post_link = post.a['href']
            post_title = post.h2.text
            if DEBUG: 
                print("post title is {0}".format(post_title))
                print("post link is {0}".format(post_link))

            post_soup = BeautifulSoup(requests.get(post_link).content, "html.parser")
            mag_link = post_soup.find_all("form")[1]["action"]
            if DEBUG:
                print("magazine link is {0}".format(mag_link))

            down_soup = BeautifulSoup(requests.get(mag_link).content, "html.parser")
            down_link = down_soup.find("iframe")["src"]
            download(down_link + "&dl=1", post_title + ".pdf")