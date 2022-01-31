#!/usr/bin/python3
#-*- coding: utf-8 -*-

import requests
import re
import os, sys, time
from bs4 import BeautifulSoup
from configparser import ConfigParser

DEBUG = True

def getTorrentsLinksByUploaderInMultipages(url, vip, pages):
    links_in_multipages = []
    result = False

    for page in range(0, int(pages)):
        url_with_page = url[:-2] + str(page + 1) + '/'
        if DEBUG: print("get links in: " + url_with_page)
        result, links = getTorrentsLinksByUploader(url_with_page, vip);
        links_in_multipages += links
    
    return result, links_in_multipages

#토렌트 링크를 얻어오는 함수 (업로더 조건 검색으로 할때)
def getTorrentsLinksByUploader(url, vip): 
    checkhours = lambda x: True if x == 'hours' else False #업로드 시간이 시간단위인지 일단위인지 체크하는 람다함수

    with requests.get(url) as page:
        if DEBUG:
            print("requests status_code is {}".format(page.status_code))
        
        if page.status_code == 200:
            list_soup = BeautifulSoup(page.content, "html.parser")

            data_div = list_soup.find("div", {"class" : "table-list-wrap"})
            data_tr= data_div.tbody.find_all("tr")

            links = []
            for tr in data_tr:
                data_item = tr.find_all("a")
                if vip == True:
                    data_item_date = tr.find("td", {"class" : "vip"}).text.split(' ')  #업로드 시간 체크 목적
                else:
                    data_item_date = tr.find("td", {"class" : "uploader"}).text.split(' ')  #업로드 시간 체크 목적
            
                links.append({
                    "name": data_item[1].string,
                    "link": data_item[1].get("href"),
                    "date": (int(data_item_date[0]), checkhours(data_item_date[1])),
               })

            return True, links

        else:
            print("requests failed")

            return False, ''

#토렌트 링크를 얻어오는 함수 (일반검색조건)
def getTorrentsLinks(url):
    checkhours = lambda x: True if len(x) < 10 else False #업로드 시간이 시간단위인지 일단위인지 체크하는 람다함수(10은 시간 글자수)

    with requests.get(url) as page:
        if DEBUG:
            print("requests status_code is {}".format(page.status_code))
        
        if page.status_code == 200:
            list_soup = BeautifulSoup(page.content, "html.parser")

            data_div = list_soup.find("div", {"class" : "table-list-wrap"})
            data_tr= data_div.tbody.find_all("tr")

            links = []
            for tr in data_tr:
                data_item = tr.find_all("a")
                data_item_date = [tr.find("td", {"class" : "coll-date"}).text, False]  #업로드 시간 체크 목적
                if checkhours(data_item_date[0]):
                    data_item_date[1] = True
            
                links.append({
                    "name": data_item[1].string,
                    "link": data_item[1].get("href"),
                    "date": data_item_date,
               })

            return True, links

        else:
            print("requests failed")

            return False, ''

#트랜스미션에 토렌트를 추가하는 함수
def addTorrentsLinks(links, postlink, howmany, transmission, host, username, password):
    get = 0
    fail = 0

    if len(links) >= howmany:
        links = links[0:howmany-1]

    for link in links:
        with requests.get(postlink + link["link"]) as link_page:
            if DEBUG:
                print("requests status_code is {}".format(link_page.status_code))

            if link_page.status_code == 200:
                link_soup = BeautifulSoup(link_page.content, "html.parser")
                link_magnet = link_soup.find("a", href=re.compile("magnet:+"))["href"]

                if DEBUG == True:
                    command = '%s %s --auth %s:%s --add "%s"' % (transmission, host, username, password, link_magnet)
                    print(command)
                else: 
                    os.system ('%s %s --auth %s:%s --add "%s"' % (transmission, host, username, password, link_magnet))

                get += 1

            else:
                fail += 1
                if DEBUG:
                    print("requests failed")
    
    if DEBUG:
        print("{} get, {} fail".format(get, fail))

    return get, fail


if __name__ == '__main__':
    if DEBUG:
        print("program is in debug mode")

    if len(sys.argv) == 2:
        config = ConfigParser()
        config.read(sys.argv[1])

        #커넥션 에러일 경우 반복
        result = False
        while result is False:
            if config['LINK'].getboolean('BYUPLOADER'):
                if config['LINK'].getboolean('MULTIPAGES'):
                    result, links = getTorrentsLinksByUploaderInMultipages(
                        config['LINK']['URL'], 
                        config['LINK'].getboolean('BYVIP'),
                        config['LINK']['PAGES']
                    )
                else:
                    result, links = getTorrentsLinksByUploader(
                        config['LINK']['URL'], 
                        config['LINK'].getboolean('BYVIP')
                    )
            else:
                result, links = getTorrentsLinks(config['LINK']['URL'])

            if result is False:
                print("getting links failed. wait 10 seconds...")
                time.sleep(10)

        if result:
            if config['LINK'].getboolean('TODAY') == True:
                temp = []
                for link in links:
                    if DEBUG: 
                        print(link)
                        print(type(link['date'][1]))
                    if link["date"][1] == True:
                        temp.append(link)
                links = temp

            if DEBUG:
                print("result is {}".format(result))
                for idx, link in enumerate(links):
                    print("link {0} is {1}".format(idx, link))

            if DEBUG is not True:
                addTorrentsLinks(
                    links,
                    config['LINK']['URL_PREFIX'],
                    config['LINK'].getint('HOWMANY'),
                    config['HOST']['TRANSMISSION'],
                    config['HOST']['HOST'], 
                    config['HOST']['USERNAME'], 
                    config['HOST']['PASSWORD'],
                )
    else:
        print("usage: {0} setting_file".format(sys.argv[0]))
