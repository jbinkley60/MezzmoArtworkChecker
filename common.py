# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv
from datetime import datetime, timedelta

ac_config = {}

def initializeLog(config):

    global ac_config

    ac_config = config


def genLog(mgenlog, display = 'No'):                  #  Write to logfile

    global ac_config
    logoutfile = ac_config['logoutfile']
    fileh = open(logoutfile, "a")                   #  open log file
    currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = fileh.write(currTime + ' - ' + mgenlog.strip() + '\n')
    if display != 'No':
        print(mgenlog.strip())
    fileh.close()

