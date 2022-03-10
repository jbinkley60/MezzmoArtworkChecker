# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv
from datetime import datetime

mezzmodbfile = ''
mezzmoposterpath = ''
csvout = ''
actordb = 'mezzmo_artwork.db'
sysarg1 = ''
if len(sys.argv) == 2:
    sysarg1 = sys.argv[1]


def getConfig():

    try:
        global mezzmodbfile, mezzmoposterpath
        print ("Mezzmo actor comparison v1.0.2")        
        fileh = open("config.txt")                                     # open the config file
        data = fileh.readline()
        dataa = data.split('#')                                        # Remove comments
        data = dataa[0].strip().rstrip("\n")                           # cleanup unwanted characters
        mezzmodbfile = data + "Mezzmo.db"
        data = fileh.readline()
        datab = data.split('#')                                        # Remove comments
        mezzmoposterpath = datab[0].strip().rstrip("\n")               # cleanup unwanted characters
        fileh.close()                                                  # close the file
        if len(mezzmodbfile) < 5 or len(mezzmoposterpath) < 5:
            print("Invalid configuration file.  Please check the config.txt file.")
            exit()
        else:
            print ("Mezzo database file location: " + mezzmodbfile)
            print ("Mezzmo artwork folder: " + mezzmoposterpath)

    except Exception as e:
        print (e)
        pass


def checkClean(sysarg):

    global csvout
    if len(sysarg) > 1 and 'clean' not in sysarg and 'csv' not in sysarg:
        print('\nThe only valid commands are -  clean and csv')
        print('\nProviding no arguments runs the artwork tracker normally.')
        print('\nclean will remove entries from all tables in artwork tracker database.')
        print('\ncsv will run the actor comparison and provide a csv file for the actorArtwork table and')
        print('an actor no match csv file which are Mezzmo actors without a Poster or UserPoster file.')
        exit()
    elif 'clean' in sysarg:
        print('\nCleaning all records from the artwork tracker database.')
        db = openActorDB() 
        db.execute('DELETE FROM actorArtwork',)
        db.execute('DELETE FROM userPosterFile',)
        db.execute('DELETE FROM posterFile',)
        db.commit()
        db.close()
        print('Artwork tracker database successfully cleaned.')        
        print('Rerun the artwork tracker to repopulate the database.')
        exit()
    elif 'csv' in sysarg:
        csvout = 'true'
        print('CSV file output selected.')


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
   
        db.commit()
        db.close()
        print ("Mezzmo check database completed.")

    except Exception as e:
        print (e)
        print ("There was a problem verifying the database file: " + actordb) 
        exit()    
      

def getMezzmo(dbfile):
    
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite

    print ("Getting Mezzmo database actor records.")                          
    db = sqlite.connect(dbfile)

    dbcurr = db.execute('SELECT Data FROM MGOFileArtist',)
    dbtuples = dbcurr.fetchall()
    del dbcurr
    db.close()

    actdb = openActorDB()
    #actdb = sqlite.connect(actordb)
    for a in range(len(dbtuples)):
        #print (dbtuples[a][0])
        pactormodify = dbtuples[a][0].lower().replace(' ', '-').replace('.','-').replace('&','-').replace("'",'-')
        actormodify = pactormodify.replace("(",'-').replace(')','-').replace('"','-').replace(',','')
        currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        curp = actdb.execute('SELECT actor FROM actorArtwork WHERE actor=?',(dbtuples[a][0],))  #  Check actorArtwork
        actortuple = curp.fetchone()
        if not actortuple and len(dbtuples[a][0]) > 0: 
            actdb.execute('INSERT into actorArtwork (dateAdded, actor, actorMatch) values (?, ?, ?)', \
            (currDateTime, dbtuples[a][0], actormodify,))     
    actdb.commit()
    curp = actdb.execute('SELECT count (*) FROM actorArtwork',)
    counttuple = curp.fetchone()
    print ("Mezzo actor records found: " + str(counttuple[0]))
    del curp
    actdb.close()


def getUserPosters(path):

    try:
        print ("Getting Mezzmo UserPoster files.") 
        actdb = openActorDB()
        userposter = path + "UserPoster\\"   
        #print (userposter) 
        listOfFiles = os.listdir(userposter)
        pattern = "*.jpg"
        for x in listOfFiles:                    
            if fnmatch.fnmatch(x, pattern):
                curp = actdb.execute('SELECT file FROM userPosterFile WHERE file=?',(x,))
                actortuple = curp.fetchone()
                if not actortuple:
                    currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    actdb.execute('INSERT into userPosterFile (dateAdded, file) values (?, ?)', \
                    (currDateTime, x,))   
                    curp = actdb.execute('SELECT actor FROM actorArtwork WHERE actorMatch=?',(x[:-4].lower(),))
                    actortuple = curp.fetchone()
                    if actortuple:
                        actdb.execute('UPDATE actorArtwork SET dateAdded=?, userPosterFile=? WHERE \
                        actorMatch=?', (currDateTime, x, x[:-4].lower()))
                        actdb.execute('UPDATE userPosterFile SET mezzmoMatch=? WHERE file=?', \
                        ('Yes', x,))
                    else:
                        actdb.execute('UPDATE userPosterFile SET mezzmoMatch=? WHERE file=?', \
                        ('No', x,))                    
        curp = actdb.execute('SELECT count (*) FROM userPosterFile',)
        counttuple = curp.fetchone()
        print ("Mezzo UserPoster files found: " + str(counttuple[0]))                 
        curp = actdb.execute('SELECT count (*) FROM userPosterFile WHERE mezzmoMatch=? ',('No',))
        counttuple = curp.fetchone()   
        print ("Mezzo UserPoster files without Mezzmo actor: " + str(counttuple[0]))    
        actdb.commit()
        del actortuple, curp, counttuple
        actdb.close()

    except Exception as e:
        print (e)
        pass


def getPosters(path):

    try:
        print ("Getting Mezzmo Poster files.") 
        actdb = openActorDB()
        userposter = path + "Poster\\"   
        #print (userposter) 
        listOfFiles = os.listdir(userposter)
        pattern = "cva_srch*.jpg"
        count = 0
        for x in listOfFiles:                    
            if fnmatch.fnmatch(x, pattern):
                curp = actdb.execute('SELECT file FROM posterFile WHERE file=?',(x,))
                actortuple = curp.fetchone()
                if not actortuple:
                    currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    actdb.execute('INSERT into posterFile (dateAdded, file) values (?, ?)', \
                    (currDateTime, x,))
                    actquery = x[9:-4].lower()              #  Remove cva-srch- and file extension
                    #print (x)
                    #print (actquery)
                    curp = actdb.execute('SELECT actor FROM actorArtwork WHERE actorMatch=?',(actquery,))
                    actortuple = curp.fetchone()
                    if actortuple:
                        actdb.execute('UPDATE actorArtwork SET dateAdded=?, posterFile=? WHERE \
                        actorMatch=?', (currDateTime, x, actquery))
                        actdb.execute('UPDATE posterFile SET mezzmoMatch=? WHERE file=?', \
                        ('Yes', x,))
                    else:
                        actdb.execute('UPDATE posterFile SET mezzmoMatch=? WHERE file=?', \
                        ('No', x,))
            count += 1
            if count % 5000 == 0:
                print (str(count) + ' Mezzmo poster files processed.')          
        curp = actdb.execute('SELECT count (*) FROM posterFile',)
        counttuple = curp.fetchone()
        print ("Mezzo Poster files found: " + str(counttuple[0]))                 
        curp = actdb.execute('SELECT count (*) FROM posterFile WHERE mezzmoMatch=? ',('No',))
        counttuple = curp.fetchone()   
        print ("Mezzo Poster files without Mezzmo actor: " + str(counttuple[0]))    
        actdb.commit()
        del actortuple, curp, counttuple
        actdb.close()

    except Exception as e:
        print (e)
        pass


def getMatches():
   
    try:
        actdb = openActorDB()
        curm = actdb.execute('select count (*) from actorArtwork where posterFile IS NULL and \
        userPosterFile IS NULL',)
        mtuple = curm.fetchone()
        if mtuple:
            print('Mezzmo actors without Poster or UserPoster file: ' + str(mtuple[0]))
        else:
            print('There was a problem determining Mezzmo actors with missing Poster and UserPoster files.')
        del curm
        actdb.close()
    except Exception as e:
        print (e)
        pass


def checkCsv(selected):

    try:
        if selected == 'true':
            if sys.version_info[0] < 3:
                print('The CSV export utility requires Python version 3 or higher')
                exit()    
            print('CSV file export beginning.')
            db = openActorDB()
            curm = db.execute('SELECT * FROM actorArtwork')
            recs = curm.fetchall()
            headers = [i[0] for i in curm.description]
            fpart = datetime.now().strftime('%H%M%S')
            filename = 'actorartwork_' + fpart + '.csv'
            writeCSV(filename, headers, recs)
            curm = db.execute('select * from actorArtwork where posterFile IS NULL and \
            userPosterFile IS NULL',)
            recs = curm.fetchall()
            headers = [i[0] for i in curm.description]
            fpart = datetime.now().strftime('%H%M%S')
            filename = 'actor_no_match_' + fpart + '.csv'
            writeCSV(filename, headers, recs)               
            del curm
            db.close()
            print('CSV file exports completed.')

    except Exception as e:
        print (e)
        pass


def writeCSV(filename, headers, recs):

    try:
        csvFile = csv.writer(open(filename, 'w', encoding='utf-8'),
                         delimiter=',', lineterminator='\n',
                         quoting=csv.QUOTE_ALL, escapechar='\\')
        csvFile.writerow(headers)     # Add the headers and data to the CSV file.
        for row in recs:
            recsencode = []
            for item in range(len(row)):
                if isinstance(row[item], int) or isinstance(row[item], float):  # Convert to strings
                    recitem = str(row[item])
                else:
                    recitem = row[item]
                recsencode.append(recitem) 
            csvFile.writerow(recsencode)               

    except Exception as e:
        print (e)
        pass


def optimizeDB():                                   # Optimize database 

    db = openActorDB()
    db.execute('REINDEX',)
    db.execute('VACUUM',)
    db.commit()    
    db.close()
    print('Mezzmo artwork tracker database optimization complete.')


#  Main routines
checkClean(sysarg1)
getConfig()
checkDatabase()
optimizeDB()
getMezzmo(mezzmodbfile)
getUserPosters(mezzmoposterpath)
getPosters(mezzmoposterpath)
getMatches()
checkCsv(csvout)
print('Mezzmo actor comparison completed successfully.')

