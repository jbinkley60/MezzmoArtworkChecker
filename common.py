# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv
from datetime import datetime, timedelta

ac_config = {}
actordb = ''

def initializeLog(config):

    global ac_config, actordb

    ac_config = config
    actordb = ac_config['actordb']


def genLog(mgenlog, display = 'No'):                  #  Write to logfile

    global ac_config
    logoutfile = ac_config['logoutfile']
    fileh = open(logoutfile, "a")                   #  open log file
    currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = fileh.write(currTime + ' - ' + mgenlog.strip() + '\n')
    if display != 'No':
        print(mgenlog.strip())
    fileh.close()


def openActorDB():

    global actordb
    
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                       
    db = sqlite.connect(actordb)

    return db




