#!/usr/bin/python
# convert json piped from rtl_sdr weatherstation
# and store in sqlite database

import sqlite3
from datetime import datetime as dt
import json
import fileinput

sqlite_file = '/var/log/temperature/weatherstation.sqlite'    # name of the sqlite database file
#sqlite_file = '/home/pi/weatherstation.sqlite'    # name of the sqlite database file
table_name = 'data'   # name of the table to be created
index_col = 'id'
date_col = 'date' # name of the date column
time_col = 'time'# name of the time column


# create new sqlite database
# Connecting to the database file
def create_database(d):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    print('creating new table')
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
        .format(tn=table_name, nf=index_col, ft='INTEGER'))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'"\
         .format(tn=table_name, cn=date_col))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'"\
         .format(tn=table_name, cn=time_col))
    for field in d:
      if field != 'time':
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
            .format(tn=table_name, cn=field, ct='REAL'))
    conn.commit()
    conn.close()

# write to sqlite database
def store_in_database(d):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    if not c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{tn}'"\
        .format(tn=table_name)).fetchone():
        create_database(d)
    c.execute("INSERT INTO {tn} ({cn}) VALUES(DATE('{thedate}'))"\
       .format(tn=table_name, idf=index_col, cn=date_col, thedate=d['time']))
    lrid = c.lastrowid
    c.execute("UPDATE {tn} SET {cn}=TIME('{thedate}') WHERE {idf}=({rid})"\
         .format(tn=table_name, idf=index_col, rid=lrid, cn=time_col, thedate=d['time']))       
    for field in d:
      if field != 'time':
         c.execute("UPDATE {tn} SET {cn}={val} WHERE {idf}=({rid})"\
              .format(tn=table_name, idf=index_col, rid=lrid, cn=field, val=d[field]))       
    conn.commit()
    conn.close()

for line in fileinput.input():
    try:
        d = json.loads(line)
        #for field in d:
        #   print(field,d[field])
        # remove non numeric and unneeded values
        d.pop("mic")
        d.pop("model")
        d.pop("id")
        store_in_database(d)
    except:
        pass
    
# test read back from database
#conn = sqlite3.connect(sqlite_file)
#conn.row_factory = sqlite3.Row
#c = conn.cursor()
#c.execute("SELECT * FROM {tn} ".\
#        format(tn=table_name))
#rows = c.fetchall()
#for row in rows:
#    print(row)       
#conn.close()
