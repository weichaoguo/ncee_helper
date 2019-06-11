#!/usr/bin/env python
#coding=utf-8



import json
import sys
import time
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
from lxml import etree
import urllib2
from bs4 import BeautifulSoup
import re



if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.ncee
    db_ncee_scores = db.school_scores
    i = 1
    while i <= 23375:
        url = 'https://data-gkcx.eol.cn/soudaxue/queryProvinceScore.html?messtype=jsonp&page=%d&size=10' % (i)
        #print url
        #time.sleep(1)
        html = ''
        try:
            response = urllib2.urlopen(url)
            html = response.read()
        except Exception as e:
            print e
            time.sleep(30)
            continue
        try:
            for school in json.loads(html.replace('null(', '').replace(');', ''))['school']:
                #print school
                school.pop('url')
                db_ncee_scores.insert(school)
        except Exception as e:
            print e
            time.sleep(30)
            continue
        print '\r%d' % i
        i = i + 1
    db_client.close()
