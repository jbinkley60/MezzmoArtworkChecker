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


def checkDatabase():

    try:
        db = openActorDB()

        db.execute('CREATE table IF NOT EXISTS actorArtwork (dateAdded TEXT, actor TEXT, actorMatch TEXT,  \
        posterFile Type TEXT, userPosterFile TEXT)')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS actor_1 ON actorArtwork (actor)')
        db.execute('CREATE INDEX IF NOT EXISTS actor_2 ON actorArtwork (actorMatch)')
        db.execute('CREATE table IF NOT EXISTS userPosterFile (dateAdded TEXT, file TEXT, mezzmoMatch TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS uposter_1 ON userPosterFile (file)')
        db.execute('CREATE table IF NOT EXISTS posterFile (dateAdded TEXT, file TEXT, mezzmoMatch TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS poster_1 ON posterFile (file)')

        db.execute('CREATE table IF NOT EXISTS actorIndex (fileID TEXT, ID TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS actorIdx_1 ON actorIndex (ID)')
        db.execute('CREATE INDEX IF NOT EXISTS actorIdx_2 ON actorIndex (fileID)')

        db.execute('CREATE table IF NOT EXISTS mezzmoFile (ID TEXT, file TEXT, title TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS mezzmof_1 ON mezzmoFile (ID)')

        db.execute('CREATE table IF NOT EXISTS mezzmoMovies (actor TEXT, actorID TEXT, posterFile TEXT, \
        userPosterFile TEXT, title TEXT, fileID TEXT, file TEXT)')
        db.execute('CREATE INDEX IF NOT EXISTS mezzmom_1 ON mezzmoMovies (actor)')


        try:                                          #  Added for v1.0.3
            db.execute('ALTER TABLE actorArtwork ADD COLUMN lastChecked TEXT')
        except:
            pass

        try:                                          #  Added for v1.0.3
            db.execute('CREATE INDEX IF NOT EXISTS actor_3 ON actorArtwork (lastChecked)')
        except:
            pass

        try:                                          #  Added for v1.0.3
            db.execute('ALTER TABLE actorArtwork ADD COLUMN checkStatus TEXT')
        except:
            pass

        try:                                          #  Added for v1.0.6
            db.execute('ALTER TABLE actorArtwork ADD COLUMN mezzmoChecked TEXT')
        except:
            pass

        try:                                          #  Added for v1.0.6
            db.execute('CREATE INDEX IF NOT EXISTS actor_4 ON actorArtwork (mezzmoChecked)')
        except:
            pass            

        try:                                          #  Added for v1.0.9
            db.execute('ALTER TABLE actorArtwork ADD COLUMN actorID TEXT')
        except:
            pass

        try:                                          #  Added for v1.0.9
            db.execute('CREATE INDEX IF NOT EXISTS actor_5 ON actorArtwork (actorID)')
        except:
            pass 

        try:                                          #  Added for v1.0.17
            db.execute('ALTER TABLE mezzmoFile ADD COLUMN TypeUID INTEGER')
        except:
            pass

        try:                                          #  Added for v1.0.17
            db.execute('ALTER TABLE mezzmoFile ADD COLUMN DateAdded TEXT')
        except:
            pass

        try:                                          #  Added for v1.0.17
            db.execute('ALTER TABLE mezzmoFile ADD AlbumID INTEGER')
        except:
            pass

        try:                                          #  Added for v1.0.17
            db.execute('ALTER TABLE mezzmoFile ADD Track INTEGER')
        except:
            pass

        try:                                          #  Added for v1.0.17
            db.execute('ALTER TABLE mezzmoFile ADD TheMovieDB_ID TEXT')
        except:
            pass

        try:                                          #  Added for v1.0.17
            db.execute('ALTER TABLE mezzmoFile ADD Description TEXT')
        except:
            pass          

        db.commit()
        db.close()
        mgenlog = 'Mezzmo check database completed.'
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        mgenlog = 'There was a problem verifying the database file: ' + actordb
        genLog(mgenlog, 'Yes')  
        exit()   


def updateMezzmoFile():                       #  Update mezzmoFile from Mezzmo MGOFile

    try:
        dbfile = ac_config['dbfile']
        try:
            from sqlite3 import dbapi2 as sqlite
        except:
            from pysqlite2 import dbapi2 as sqlite

        actdb = openActorDB()
        db = sqlite.connect(dbfile) 
        mgenlog = 'Getting Mezzmo database file records.'
        genLog(mgenlog, 'Yes')    
        dbcurr = db.execute('SELECT ID, File, Title, TypeUID, DateAdded, AlbumID, Track,            \
        TheMovieDB_ID, Description FROM MGOFile',)
        dbtuples = dbcurr.fetchall()
        db.close()
        del dbcurr
        for a in range(len(dbtuples)):
            actdb.execute('INSERT into mezzmoFile (ID, file, title, TypeUID, DateAdded, AlbumID,     \
            Track, TheMovieDB_ID, Description) values (?, ?, ?, ?, ?, ?, ?, ?, ?)', (dbtuples[a][0], \
            dbtuples[a][1], dbtuples[a][2], dbtuples[a][3], dbtuples[a][4], dbtuples[a][5],          \
            dbtuples[a][6], dbtuples[a][7], dbtuples[a][8],))
        actdb.commit()
        actdb.close()
        mgenlog = 'Finished getting Mezzmo file records.'
        genLog(mgenlog, 'Yes') 


    except Exception as e:
        print (e)
        mgenlog = 'There was a problem updating the mezzmoFile table from Mezzmo'
        genLog(mgenlog, 'Yes')  
        exit()   
