# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv
from datetime import datetime
import actor_imdb

mezzmodbfile = ''
mezzmoposterpath = ''
csvout = ''
imageout = ''
badimage = ''
imdb_key = ''
imdb_count = '20'
imdb_limit = '500'
actordb = 'mezzmo_artwork.db'
sysarg1 = ''
sysarg2 = ''
if len(sys.argv) == 2:
    sysarg1 = sys.argv[1]
if len(sys.argv) == 3:
    sysarg1 = sys.argv[1]    
    sysarg2 = sys.argv[2]

def getConfig():

    try:
        global mezzmodbfile, mezzmoposterpath, imdb_key, imdb_count, imdb_limit
        print ("Mezzmo actor comparison v1.0.4")        
        fileh = open("config.txt")                                     # open the config file
        data = fileh.readline()
        dataa = data.split('#')                                        # Remove comments
        data = dataa[0].strip().rstrip("\n")                           # cleanup unwanted characters
        mezzmodbfile = data + "Mezzmo.db"
        data = fileh.readline()
        datab = data.split('#')                                        # Remove comments
        mezzmoposterpath = datab[0].strip().rstrip("\n")               # cleanup unwanted characters
        data = fileh.readline()                                        # Get IMDB API key
        if data != '':
            datac = data.split('#')                                    # Remove comments
            imdb_key = datac[0].strip().rstrip("\n")                   # cleanup unwanted characters
            data = fileh.readline()                                    # Get IMDB query count
            if data != '':
                datad = data.split('#')                                # Remove comments
                count = datad[0].strip().rstrip("\n")                  # cleanup unwanted characters
                if int(count) > int(imdb_limit):                       # Set IMDB limit              
                    imdb_count = int(imdb_limit)
                else:
                    imdb_count = count

        fileh.close()                                                  # close the file

        if len(mezzmodbfile) < 5 or len(mezzmoposterpath) < 5:
            print("Invalid configuration file.  Please check the config.txt file.")
            exit()
        else:
            print ("Mezzo database file location: " + mezzmodbfile)
            print ("Mezzmo artwork folder: " + mezzmoposterpath)

        #print(imdb_key)
        #print(imdb_count)

    except Exception as e:
        print (e)
        pass


def checkClean(sysarg):

    global csvout, imageout, badimage
    if len(sysarg) > 1 and 'clean' not in sysarg and 'csv' not in sysarg and 'images' not in sysarg and \
    'bad' not in sysarg:
        print('=========================================================================================')
        print('The only valid commands are -  clean, csv, images and bad')
        print('\nProviding no arguments runs the artwork tracker normally.')
        print('\nclean will remove entries from all tables in artwork tracker database.')
        print('\ncsv will run the actor comparison and provide a csv file for the actorArtwork table and')
        print('an actor no match csv file which are Mezzmo actors without a Poster or UserPoster file.')
        print('\nimages will fetch missing actor images. A valid IMDB API Key must be in the config file.')
        print('\nbad followed by the image file name (without file extension) will mark an actor as having')
        print('a bad image on IMDB and will not attempt to retrieve this image again from IMDB.  ')
        print('Example:   mezzmo_actor.py bad john-doe     ') 
        print('=========================================================================================')
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
    elif 'images' in sysarg:
        imageout = 'true'
        print('IMDB image fetching selected.')
    elif 'bad' in sysarg:
        badimage = 'true'
        print('Bad image file marking selected.')


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

        try:
            db.execute('ALTER TABLE actorArtwork ADD COLUMN lastChecked TEXT')
            db.execute('ALTER TABLE actorArtwork ADD COLUMN checkStatus TEXT')
            db.execute('CREATE INDEX IF NOT EXISTS actor_3 ON actorArtwork (lastChecked)')
        except:       
            pass

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
                currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if not actortuple:
                    currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    actdb.execute('INSERT into userPosterFile (dateAdded, file) values (?, ?)', \
                    (currDateTime, x,))   
                    curm = actdb.execute('SELECT actor FROM actorArtwork WHERE actorMatch=?',(x[:-4].lower(),))
                    acttuple = curm.fetchone()
                    if acttuple:
                        actdb.execute('UPDATE actorArtwork SET dateAdded=?, userPosterFile=?,   \
                        lastChecked=?, checkStatus=? WHERE actorMatch=?', (currDateTime, x,     \
                        currDateTime, 'Found on Mezzmo', x[:-4].lower()))
                        actdb.execute('UPDATE userPosterFile SET mezzmoMatch=? WHERE file=?',   \
                        ('Yes', x,))
                    else:
                        actdb.execute('UPDATE userPosterFile SET mezzmoMatch=? WHERE file=?',   \
                        ('No', x,)) 
                else:
                    actdb.execute('UPDATE actorArtwork SET userPosterFile=?, lastChecked=?,     \
                    checkStatus=? WHERE actorMatch=?', (x, currDateTime,'Found on Mezzmo',      \
                    x[:-4].lower()))
                    curm = actdb.execute('SELECT actor FROM actorArtwork WHERE actorMatch=?',(x[:-4].lower(),))
                    acttuple = curm.fetchone()
                    if acttuple:              
                        actdb.execute('UPDATE userPosterFile SET mezzmoMatch=? WHERE file=?',   \
                        ('Yes', x,))
                    else:
                        actdb.execute('UPDATE userPosterFile SET mezzmoMatch=? WHERE file=?',   \
                        ('No', x,))

        curp = actdb.execute('SELECT count (*) FROM userPosterFile',)
        counttuple = curp.fetchone()
        print ("Mezzo UserPoster files found: " + str(counttuple[0]))                 
        curp = actdb.execute('SELECT count (*) FROM userPosterFile WHERE mezzmoMatch=? ',('No',))
        counttuple = curp.fetchone()   
        print ("Mezzo UserPoster files without Mezzmo actor: " + str(counttuple[0]))    
        actdb.commit()
        del actortuple, curp, counttuple, curm, acttuple
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
                currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                actquery = x[9:-4].lower()              #  Remove cva-srch- and file extension
                if not actortuple:
                    actdb.execute('INSERT into posterFile (dateAdded, file) values (?, ?)',      \
                    (currDateTime, x,))
                    #print (x)
                    #print (actquery)
                    curm = actdb.execute('SELECT actor FROM actorArtwork WHERE actorMatch=?',(actquery,))
                    acttuple = curm.fetchone()
                    if acttuple:
                        actdb.execute('UPDATE actorArtwork SET dateAdded=?, posterFile=?,       \
                        lastChecked=?, checkStatus=? WHERE actorMatch=?', (currDateTime, x,     \
                        currDateTime, 'Found on Mezzmo', actquery))
                        actdb.execute('UPDATE posterFile SET mezzmoMatch=? WHERE file=?',       \
                        ('Yes', x,))
                    else:
                        actdb.execute('UPDATE posterFile SET mezzmoMatch=? WHERE file=?',       \
                        ('No', x,))
                else:
                    actdb.execute('UPDATE actorArtwork SET posterFile=?, lastChecked=?,         \
                    checkStatus=? WHERE actorMatch=?', (x, currDateTime,'Found on Mezzmo', actquery))  
                    curm = actdb.execute('SELECT actor FROM actorArtwork WHERE actorMatch=?',(actquery,))
                    acttuple = curm.fetchone()
                    if acttuple:
                        actdb.execute('UPDATE posterFile SET mezzmoMatch=? WHERE file=?',       \
                        ('Yes', x,))
                    else:
                        actdb.execute('UPDATE posterFile SET mezzmoMatch=? WHERE file=?',       \
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
        del actortuple, curp, counttuple, curm, acttuple
        actdb.close()

    except Exception as e:
        print (e)
        pass


def getMatches():
   
    try:
        actdb = openActorDB()
        currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        curm = actdb.execute('select count (*) from actorArtwork where posterFile IS NULL and        \
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
        csvFile = csv.writer(open(filename, 'w', encoding = 'utf-8'),
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


def getIMDBimages():                                         #  Fetch missing actor images from IMDB

    try:
        global imdb_key, imdb_count, imageout
        if imageout == 'true':
            print('IMDB image fetching beginning.')
            db = openActorDB()
            curp = db.execute('SELECT actor, checkStatus FROM actorArtwork ORDER BY lastChecked    \
            ASC LIMIT ?', (int(imdb_count),))
            actortuple = curp.fetchall()        
            #print ('Records returned: ' + str(len(actortuple)))
            for a in range(len(actortuple)):
                actorname = actortuple[a][0]
                cstatus = actortuple[a][1]
                #print(actorname)
                imgresult = actor_imdb.getImage(imdb_key, actorname, cstatus)
                currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #print(imgresult)
                if imgresult == 'imdb_error':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'IMDB error', actorname,))
                    print('Error fetching IMDB image for: ' + actorname)
                elif imgresult == 'imdb_busy':
                    print('IMDB fetching skipped. Server busy: ' + actorname)
                elif imgresult == 'imdb_found':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'Found at IMDB', actorname,))
                elif imgresult == 'imdb_nopicture':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'Not artwork at IMDB', actorname,))
                elif imgresult == 'imdb_notfound':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'No actor match at IMDB', actorname,))
                elif imgresult == 'imdb_bad' or imgresult == 'imdb_mezzmo' or imgresult == 'imdb_found':
                    db.execute('UPDATE actorArtwork SET lastChecked=? WHERE actor=?', (currDateTime,  \
                    actorname,))
                elif imgresult == 'imdb_badkey':
                    print('IMDB image fetching stopping.')
                    break               
                db.commit()                                    
            db.close()
            print('IMDB image fetching completed.')

    except Exception as e:
        print (e)
        pass


def checkBad(selected):                             # Mark bad image file

    try:
        global badimage, sysarg2
        if badimage == 'true':
            if len(sysarg2) < 4:
                print('\nValid image file not entered.  Please resubmit command with valid file.')
                exit()
            db = openActorDB()
            curp = db.execute('SELECT actorMatch FROM actorArtwork WHERE actorMatch=?', (sysarg2,))
            actortuple = curp.fetchone() 
            if actortuple:
                currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')                
                db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actorMatch=?',  \
                (currDateTime,'Bad Image', sysarg2,))
                db.commit()
                print('Image file successfully marked as bad.' + sysarg2)
            else:
                print('The image file name entered was not found in the Mezzmo actor database.')
            del curp
            db.close()
            exit()

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
checkBad(sysarg1)
getConfig()
checkDatabase()
optimizeDB()
getMezzmo(mezzmodbfile)
getUserPosters(mezzmoposterpath)
getPosters(mezzmoposterpath)
getMatches()
getIMDBimages()
checkCsv(csvout)
print('Mezzmo actor comparison completed successfully.')

