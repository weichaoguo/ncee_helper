#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from Tkinter import *
import Tkinter as ttk 
from ttk import *
import tkMessageBox
#from tkintertable import TableCanvas, TableModel
import sqlite3

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        tkMessageBox.showerror("Error","打开数据库失败")
        #print e
    return None

def get_student_type(conn):
    student_types = []
    c = conn.cursor()
    c.execute("SELECT DISTINCT studenttype FROM score")
    for student_type in c.fetchall():
    	student_types.append(student_type[0])
    return student_types

def get_batch(conn):
    batches = []
    c = conn.cursor()
    c.execute("SELECT DISTINCT batch FROM score")
    for batch in c.fetchall():
    	batches.append(batch[0])
    return batches

def get_specialty(conn):
    specialties = ['全部']
    c = conn.cursor()
    #c.execute("SELECT DISTINCT specialtyname FROM score")
    #for specialty in c.fetchall():
    #	specialties.append(specialty[0])
    return specialties

def get_year(conn):
    years = []
    c = conn.cursor()
    c.execute("SELECT DISTINCT year FROM score")
    for year in c.fetchall():
    	years.append(year[0])
    return years

def get_top_school(conn, year, studenttype, batch, n):
    schools = []
    c = conn.cursor()
    c.execute("SELECT DISTINCT schoolname FROM school_score where year=? AND studenttype=? AND batch=? ORDER BY varscore DESC LIMIT ?", (year, studenttype, batch, n))
    for school in c.fetchall():
        schools.append(school[0])
    return schools

def get_batch_line(conn, year, studenttype, batch):
    if batch == u'本科提前批':
        batch = u'一批'
    c = conn.cursor()
    c.execute("SELECT score FROM batch_line WHERE year=? AND studenttype=? AND batch=?", (year, studenttype, batch))
    batch_line = c.fetchone()
    if batch_line:
        return batch_line[0]
    else:
        return None

def get_suggestion_by_rank(conn, year, studenttype, specialty, batch, rank):
    schoolnames = []
    #print year, studenttype, rank
    c = conn.cursor()
    c.execute("SELECT min(score) FROM score_ranks WHERE year=? AND studenttype=? AND ranks<?", (studenttype, year, rank))
    res = c.fetchone()
    #print res
    score = res[0] - 1
    range_low = score - 40
    range_up = score + 10
    #print year,studenttype,specialty,batch,range_low,range_up
    if specialty == u'全部':
        c.execute("SELECT DISTINCT schoolname FROM school_score WHERE year=? AND studenttype=? AND batch=? AND varscore>? AND varscore<?", (year, studenttype, batch, range_low, range_up))
    else:
        c.execute("SELECT DISTINCT schoolname FROM score WHERE year=? AND studenttype=? AND specialtyname=? AND batch=? AND varscore>? AND varscore<?", (year, studenttype, specialty, batch, range_low, range_up))
    for schoolname in c.fetchall():
        #print schoolname[0]
        schoolnames.append(schoolname[0])
    return schoolnames

def get_suggestion_by_score(conn, year, studenttype, specialty, batch, batch_line, range_low, range_up):
    schoolnames = []
    line_delta = get_batch_line(conn, year, studenttype, batch) - batch_line
    range_low = range_low + line_delta
    range_up = range_up + line_delta
    #print get_batch_line(conn, year, studenttype, batch)
    #print year,studenttype,specialty,batch,range_low,range_up
    c = conn.cursor()
    if specialty == u'全部':
        c.execute("SELECT DISTINCT schoolname FROM school_score WHERE year=? AND studenttype=? AND batch=? AND varscore>? AND varscore<?", (year, studenttype, batch, range_low, range_up))
    else:
        c.execute("SELECT DISTINCT schoolname FROM score WHERE year=? AND studenttype=? AND specialtyname=? AND batch=? AND varscore>? AND varscore<?", (year, studenttype, specialty, batch, range_low, range_up))
    for schoolname in c.fetchall():
        #print schoolname[0]
        schoolnames.append(schoolname[0])
    return schoolnames

def get_result_table(conn, studenttype, schoolnames, years, specialty):
    results = {}
    c = conn.cursor()
    for schoolname in schoolnames:
    	results[schoolname] = {}
        #results[schoolname]['学校名称'] = schoolname.encode('UTF-8')
        for year in years:
            if specialty == u'全部':
                c.execute("SELECT CAST(ROUND(AVG(varscore)) as integer), MIN(minscore), MAX(maxscore) FROM school_score WHERE year=? AND studenttype=? AND schoolname=?", (year, studenttype, schoolname))
                score = c.fetchone()
                results[schoolname][str(year)] = "%s/%s/%s" % score
            else: 
                c.execute("SELECT CAST(ROUND(AVG(varscore)) as integer), MIN(minscore), MAX(maxscore) FROM score WHERE year=? AND studenttype=? AND schoolname=? AND specialtyname=?", (year, studenttype, schoolname, specialty))
                results[schoolname][str(year)] =  "%s/%s/%s" % score
    return results

db_file = 'ncee.db'
if not os.path.exists(db_file):
    tkMessageBox.showerror("Error","数据库文件不存在")
    sys.exit(1)
conn = create_connection(db_file)
if conn is None:
    sys.exit(1)
student_types = get_student_type(conn)
#batches = get_batch(conn)
batches = ['本科提前批', '一批', '二批']
specialties = get_specialty(conn)
years = get_year(conn)

# window layout

root = Tk()
root.title("黑龙江省高考志愿填报助手")
# this removes the maximize button
root.resizable(0,0)
root.geometry('900x675')

mainframe = Frame(root)
mainframe.pack()

var_student_type = StringVar(root)
var_batch = StringVar(root)
var_specialty = StringVar(root)
var_score = IntVar(root)
var_batch_line = IntVar(root)
var_range_low = IntVar(root)
var_range_up = IntVar(root)

introframe = Frame(mainframe)
introframe.pack()
Label(introframe, text="说明：\n1、使用名次或指定分数区间筛选报考院校。省控线指对应的本科一批、二批划定分数线\n2、指定专业后，筛选使用分数均为该专业录取分数，专业分数数据不全请谨慎使用！默认全部表示不筛选专业。\n3、选定多个参考年份的含义是筛选出的院校在所有选定的参考年份都满足条件，2017年数据不全请谨慎使用\n5、筛选结果表中三个分数分别为：平均分/最低分/最高分，0或--或None表示缺少该数据或没有招生\n\n").grid(row = 0, columnspan = 20)

#search settings
settingframe = Frame(mainframe)
#settingframe.grid(row=1, columnspan=20)
settingframe.pack()

option_student_type = OptionMenu(settingframe, var_student_type, student_types[1], *student_types)
Label(settingframe, text="科类").grid(row = 1, column = 0)
option_student_type.config(width=5)
option_student_type.grid(row = 1, column =1)
#var_student_type.set(student_types[0])

var_score.set('')
Label(settingframe, text='名次').grid(row = 1, column = 2)
Entry(settingframe, textvariable=var_score, width=5).grid(row = 1, column = 3)

option_batch = OptionMenu(settingframe, var_batch, batches[1], *batches)
Label(settingframe, text="批次").grid(row = 1, column = 4)
option_batch.config(width = 5)
option_batch.grid(row = 1, column =5)
#var_batch.set(batches[0])

var_batch_line.set('')
Label(settingframe, text='省控线').grid(row = 1, column = 6)
Entry(settingframe, textvariable=var_batch_line, width=5).grid(row = 1, column = 7)

option_specialty = OptionMenu(settingframe, var_specialty, specialties[0], *specialties)
Label(settingframe, text="专业").grid(row = 1, column = 8)
option_specialty.config(width = 5)
option_specialty.grid(row = 1, column = 9)
#var_specialty.set(specialties[0])

var_range_low.set('')
var_range_up.set('')
Label(settingframe, text='分数区间').grid(row = 2, column = 0)
Entry(settingframe, textvariable=var_range_low, width=5).grid(row = 2, column = 1)
Label(settingframe, text='~').grid(row = 2, column = 2)
Entry(settingframe, textvariable=var_range_up, width=5).grid(row = 2, column = 3)

var_year = []
i = 0
Label(settingframe, text="参考年份").grid(row = 2, column = 5)
years.sort(reverse=True)
for year in years:
    var_year.append(IntVar(root))
    if i == 0:
        var_year[i].set(1)
    Checkbutton(settingframe, text=year, variable=var_year[i], onvalue=1, offvalue=0).grid(row = 2, column = (6 + i))
    i = i + 1

#search results
resultframe = Frame(mainframe, height=500)
#resultframe.grid(row = 2)
resultframe.pack(fill='both',expand='false')
#model = TableModel()
#last_schools = 10
#last_years = len(years)
top_schools = get_top_school(conn, 2017, u'理科', u'一批', 20)
results = get_result_table(conn, u'理科', top_schools, years, u'全部')
#print results
#for year in selected_years:
#    model.addColumn(str(year))
#model.importDict(results)
#table = TableCanvas(resultframe, model=model, editable=False, rowselectedcolor='yellow', rowheaderwidth=200, showkeynamesinheader=True)
#table = TableCanvas(resultframe, model=model, editable=False, rowselectedcolor='yellow')
#table.createTableFrame()
#table.grid(row = 1, column = 1)
#table.redrawTable()
tree = Treeview(resultframe, columns=tuple(years), height=450, selectmode='browse')
tree.pack()
#tree['columns'] = tuple(selected_years)

def treeview_sort_column(tv, col, reverse): 
    l = [(tv.set(k, col), k) for k in tv.get_children('')]  
    #print(tv.get_children(''))  
    l.sort(reverse=reverse)
    # rearrange items in sorted positions  
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)  
        #print(k)

def show_results(selected_years, results):
    for item in tree.get_children():
        tree.delete(item)
    tree['columns'] = tuple(selected_years)
    for year in selected_years:
        tree.heading(year, text="%d年" % year) 
        tree.column(year, width=80, anchor='center')
    i = 0
    for schoolname in results:
        t = []
        for year in selected_years:
            t.append(results[schoolname][str(year)])
        tree.insert("",i,text=schoolname ,values=tuple(t))
        i = i + 1
    treeview_sort_column(tree, selected_years[0], True)

show_results(years, results)

def join_schools(schoolnames, selected_years):
    schoolnames['join'] = schoolnames[selected_years[0]]
    for year in selected_years:
        #print year
        schoolnames['join'] = list(set(schoolnames['join']).intersection(set(schoolnames[year])))
        #for schoolname in schoolnames[year]:
        #    print schoolname
        #print 'join'
        #for schoolname in schoolnames['join']:
        #    print schoolname
    return schoolnames['join']

#print join_schools({1:[1,3,4],2:[2,3,4],3:[1,2,4]}, [1,2,3])

def search():
    by_rank = False
    try:
        rank = var_score.get()
        by_rank = True
        if (rank <= 0):
            tkMessageBox.showerror('Error', '无效的名次！')
            return
    except Exception as e:
        #print score, batch_line, range_low, range_up, e
        try:
            batch_line = var_batch_line.get()
            range_low = var_range_low.get()
            range_up = var_range_up.get()
            if (batch_line < 0 or batch_line > 750):
                tkMessageBox.showerror('Error', '无效的省控线！')
                return
            if (range_low < 0 or range_low > 750 or range_up < 0 or range_up >750 or range_low > range_up or range_up - range_low > 100):
                tkMessageBox.showerror('Error', '无效或过大的分数范围！')
                return
        except Exception as e:
           
            tkMessageBox.showerror('Error', '请输入正确的查询信息！')
            return

    selected_years = []
    for i in range(0, len(years)):
        if var_year[i].get() == 1:
            selected_years.append(years[i])
    if len(selected_years) == 0:
        tkMessageBox.showerror('Error', '请至少选择一个参考年份！')
        return
    schoolnames = {}
    for year in selected_years:
        if by_rank:
            schoolnames[year] = get_suggestion_by_rank(conn, year, var_student_type.get(), var_specialty.get(), var_batch.get(), rank)
        else:
            schoolnames[year] = get_suggestion_by_score(conn, year, var_student_type.get(), var_specialty.get(), var_batch.get(), batch_line, range_low, range_up)
    
    results = get_result_table(conn, var_student_type.get(), join_schools(schoolnames, selected_years), selected_years, var_specialty.get())
    show_results(selected_years, results)

Button(settingframe, text='查询', command=search).grid(row = 1, column = 12)

root.mainloop()
