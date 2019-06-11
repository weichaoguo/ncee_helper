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
import sqlite3


if __name__ == '__main__':
    db_client = MongoClient('localhost', 27017)
    db = db_client.ncee
    db_ncee_scores = db.school_scores
    conn = sqlite3.connect('ncee1.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE score(schoolid integer, schoolname text, localprovince text, province text, studenttype text, batch text, year integer, varscore integer, minscore integer, maxscore integer, num integer, fencha integer, provincescore integer)''')
    for score in db_ncee_scores.find({'localprovince':'河北'}, no_cursor_timeout=True):
        if score['batch'] == u"本科一批":
            score['batch'] = u"一批"
        if score['batch'] == u"本科二批":
            score['batch'] = u"二批"
        s = (0, score['schoolname'], score['localprovince'], '--', score['studenttype'], score['batch'], score['year'], score['var'], score['min'], score['max'], score['num'], 0, 0)
        #print s
        try:
            c.execute("SELECT COUNT(*) from score WHERE schoolname=? AND year=? AND localprovince=? AND studenttype=?;", (score['schoolname'], score['year'], score['localprovince'], score['studenttype']))
            res = c.fetchone()
            if res[0] == 0:
                c.execute("INSERT INTO score VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", s)
        except Exception as e:
            for i in score:
                if isinstance(score[i], list):
                    if i == 'var':
                        score[i] = score['var_score']
                    else:
                        score[i] = 0
            print score['schoolname']
            ss = (0, score['schoolname'], score['localprovince'], '--', score['studenttype'], score['batch'], score['year'], score['var'], score['min'], score['max'], score['num'], 0, 0)
            c.execute("INSERT INTO score VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", ss)
    conn.commit()
    conn.close()
    db_client.close()
