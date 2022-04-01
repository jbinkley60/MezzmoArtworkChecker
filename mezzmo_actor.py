# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv
from datetime import datetime, timedelta
import actor_imdb, actor_tmdb

mezzmodbfile = ''
mezzmoposterpath = ''
lastime = ''
csvout = ''
imageout = ''
badimage = ''
imdb_key = ''
imdb_count = '20'
imdb_limit = '1000'
tmdb_key = ''
tmdb_count = '20'
tmdb_limit = '1000'
tmdbact = imdbact = 0
actordb = 'mezzmo_artwork.db'
sysarg1 = ''
sysarg2 = ''
if len(sys.argv) == 2:
    sysarg1 = sys.argv[1].lower()
if len(sys.argv) == 3:
    sysarg1 = sys.argv[1].lower()    
    sysarg2 = sys.argv[2].lower()


def getConfig():

    try:
        global mezzmodbfile, mezzmoposterpath, imdb_key, imdb_count, imdb_limit
        global tmdb_key, tmdb_count, tmdb_limit
        print ("Mezzmo actor comparison v1.0.7")        
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
        data = fileh.readline()                                        # Get IMDB query count
        if data != '':
            datad = data.split('#')                                    # Remove comments
            count = datad[0].strip().rstrip("\n")                      # cleanup unwanted characters
        if int(count) > int(imdb_limit) or int(imdb_count) > int(imdb_limit):       # Set IMDB limit              
            imdb_count = int(imdb_limit)
        elif sysarg2 == '': 
            imdb_count = count
        data = fileh.readline()                                        # Get TMDB API key
        if data != '':
            datad = data.split('#')                                    # Remove comments
            tmdb_key = datad[0].strip().rstrip("\n")                   # cleanup unwanted characters
        data = fileh.readline()                                        # Get TMDB query count
        if data != '':
            datae = data.split('#')                                    # Remove comments
            count = datae[0].strip().rstrip("\n")                      # cleanup unwanted characters
        if int(count) > int(tmdb_limit) or int(tmdb_count) > int(tmdb_limit):       # Set TMDB limit              
            tmdb_count = int(tmdb_limit)
            print('TMDB query count exceeded maximum.  Reset to ' + str(tmdb_limit))
        elif sysarg2 == '':
            tmdb_count = count
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


def checkClean(sysarg, sysargc):

    global csvout, imageout, badimage, imdb_count, tmdb_count, sysarg2
    if len(sysarg) > 1 and 'clean' not in sysarg and 'csv' not in sysarg and 'images' not in sysarg and \
    'bad' not in sysarg:
        displayHelp()
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
        print('TMDB image fetching selected.')
        try:
            imdb_count = tmdb_count = int(sysargc)
            print('TMDB query count entered: ' + sysargc)              
        except:
            if sysargc != '':
                print('The images query count was not a valid number.  Defaulting to config.txt values.')
                sysarg2 = ''      
    elif 'bad' in sysarg:
        badimage = 'true'
        print('Bad image file marking selected.')


def displayHelp():                                 #  Command line help menu display

        print('\n=========================================================================================')
        print('\nThe only valid commands are -  clean, csv, images and bad  \n\nExample:  mezzmo_actor.py images')
        print('\n         -\tProviding no arguments runs the artwork tracker normally.')
        print('\nclean    -\tWill remove entries from all tables in artwork tracker database.')
        print('\ncsv      -\tWill run the actor comparison and provide a csv file for the actorArtwork') 
        print('\t\ttable and an actor no match csv file which are Mezzmo actors without')
        print('\t\ta Poster or UserPoster file.')
        print('\nimages   -\tWill fetch missing actor images. TMDB will ge attempted first and if a valid ')
        print('\t\tIMDB API Key is found in the config file, IMDB will then be checked.')
        print('\t\tYou can also enter an optional query count value with images')
        print('\n\t\tExample:   mezzmo_actor.py images 100     (Perform 100 TMDB image queries) ') 
        print('\nbad      - \tFollowed by the image file name will mark an actor as having a bad image')
        print('\t\tand image checking on TMDB and IMDB will be skipped for this actor.')
        print('\n\t\tExample:   mezzmo_actor.py bad john-doe   (File extension is optional)  ') 
        print('\n=========================================================================================')



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
    actdb.execute('UPDATE actorArtwork SET mezzmoChecked = NULL',)    #  Clear Mezzmo match         
    actdb.commit()
    for a in range(len(dbtuples)):
        #print (dbtuples[a][0])
        pactormodify = dbtuples[a][0].lower().replace(' ', '-').replace('.','-').replace('&','-').replace("'",'-')
        actormodify = pactormodify.replace("(",'-').replace(')','-').replace('"','-').replace(',','')
        currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        curp = actdb.execute('SELECT actor FROM actorArtwork WHERE actor=?',(dbtuples[a][0],))  #  Check actorArtwork
        actortuple = curp.fetchone()
        if not actortuple and len(dbtuples[a][0]) > 0: 
            actdb.execute('INSERT into actorArtwork (dateAdded, actor, actorMatch, mezzmoChecked) values \
            (?, ?, ?, ?)', (currDateTime, dbtuples[a][0], actormodify, 'Yes',))
        else:
            actdb.execute('UPDATE actorArtwork SET mezzmoChecked=? WHERE actor=?', ('Yes', dbtuples[a][0],))
    actdb.execute('UPDATE actorArtwork SET mezzmoChecked=? WHERE mezzmoChecked IS NOT ?', ('Deleted','Yes',))
             
    actdb.commit()
    curp = actdb.execute('SELECT count (*) FROM actorArtwork WHERE mezzmoChecked IS NOT ?', ('Deleted',))
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
        actdb.execute('DELETE FROM userPosterFile WHERE mezzmoMatch=?', ('No',))
        actdb.commit() 
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
  
        actdb.commit()
        del actortuple, curp, curm, acttuple
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
 
        actdb.commit()
        del actortuple, curp, curm, acttuple
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
        global imdb_key, imdb_count, imageout, imdbact
        busycount = 0
        if imageout == 'true':
            print('\nIMDB image fetching beginning.')
            db = openActorDB()
            curp = db.execute('SELECT actor, checkStatus FROM actorArtwork ORDER BY   \
            lastChecked DESC LIMIT ?', (int(imdb_count),))
            actortuple = curp.fetchall()        
            #print ('Records returned: ' + str(len(actortuple)))
            for a in range(len(actortuple)):
                actorname = actortuple[a][0]
                cstatus = actortuple[a][1]
                #print(actorname)
                if busycount == 3:                          # Stop after 3 consecutive busy responses
                    print('\nThe IMDB server appears to be busy or down.  Please try again later.\n')
                    break
                imgresult = actor_imdb.getImage(imdb_key, actorname, cstatus)
                currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #print(imgresult)
                #print('Busy count: ' + str(busycount))
                if imgresult == 'imdb_error':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'IMDB error', actorname,))
                    print('Error fetching IMDB image for: ' + actorname)
                    busycount += 1
                elif imgresult == 'imdb_busy':
                    print('IMDB fetching skipped. Server busy: ' + actorname)
                    busycount += 1
                elif imgresult == 'imdb_found':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'Found at IMDB', actorname,))
                    busycount = 0
                    imdbact += 1
                elif imgresult == 'imdb_nopicture':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'No artwork at IMDB', actorname,))
                    busycount = 0
                elif imgresult == 'imdb_notfound':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'No actor match at IMDB', actorname,))
                    print('IMDB actor not found in database: ' + actorname)
                    busycount = 0
                elif imgresult == 'imdb_bad' or imgresult == 'imdb_mezzmo' or imgresult ==            \
                    'imdb_found' or imgresult == 'tmdb_found':
                    db.execute('UPDATE actorArtwork SET lastChecked=? WHERE actor=?', (currDateTime,  \
                    actorname,))
                elif imgresult == 'imdb_badkey':
                    print('IMDB image fetching stopping. Invalid API key.')
                    break               
                db.commit()                                    
            db.close()
            print('IMDB image fetching completed.')

    except Exception as e:
        print (e)
        pass


def getTMDBimages():                                         #  Fetch missing actor images from TMDB

    try:
        global tmdb_key, tmdb_count, imageout, tmdbact
        if imageout == 'true':
            print('\nTMDB image fetching beginning.')
            db = openActorDB()
            #curp = db.execute('SELECT actor, lastchecked, checkStatus FROM actorArtwork ORDER BY   \
            #lastChecked ASC LIMIT ?', (int(tmdb_count),))
            curp = db.execute('SELECT actor, lastchecked, checkStatus FROM actorArtwork WHERE      \
            checkStatus IS NULL OR checkStatus NOT LIKE ? ORDER BY lastChecked ASC LIMIT ?',       \
            ('Found on Mezzmo', int(tmdb_count),))
            actortuple = curp.fetchall()        
            #print ('Records returned: ' + str(len(actortuple)))
            for a in range(len(actortuple)):
                actorname = actortuple[a][0]
                pchecktime = actortuple[a][1]
                cstatus = actortuple[a][2]
                #print(actorname)
                currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                #checktime = (datetime.now() + timedelta(days=-14)).strftime('%Y-%m-%d %H:%M:%S')
                #if pchecktime != None and checktime > pchecktime:
                #    cstatus = ''
                #print(checktime)
                imgresult = actor_tmdb.getImage(tmdb_key, actorname, cstatus)
                #print(imgresult)
                if imgresult == 'tmdb_error':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'TMDB error', actorname,))
                    print('Error fetching TMDB image for: ' + actorname)
                elif imgresult == 'tmdb_busy':
                    print('TMDB fetching skipped. Server busy: ' + actorname)
                elif imgresult == 'tmdb_found':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'Found at TMDB', actorname,))
                    tmdbact += 1
                elif imgresult == 'tmdb_nopicture':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'No artwork at TMDB', actorname,))
                elif imgresult == 'tmdb_notfound':
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actor=?',  \
                    (currDateTime,'No actor match at TMDB', actorname,))
                    print('TMDB actor not found in database: ' + actorname)
                elif imgresult == 'tmdb_bad' or imgresult == 'tmdb_mezzmo' or imgresult == 'tmdb_found':
                    db.execute('UPDATE actorArtwork SET lastChecked=? WHERE actor=?', (currDateTime,  \
                    actorname,))
                elif imgresult == 'tmdb_badkey':
                    print('TMDB image fetching stopping. Invalid API key.')
                    break               
                db.commit()                                    
            db.close()
            print('TMDB image fetching completed.')

    except Exception as e:
        print (e)
        pass


def checkBad():                                            # Mark bad image file

    try:
        global badimage, sysarg2
        badlist = []
        badfile = sysarg2.lower().split('.')[0]            # Handle file extension and mixed case
        #print(badfile)
        if badimage == 'true':
            #if len(badfile) < 4:
            if badfile:                                    # Append user entry
                badlist.append(badfile)                    # Process badfiles
            badresult = updateBad(badlist)
            if badresult == 'good':
                print('Bad file processing completed.')
            else:
                print('There was a problem completing the Bad file processing.')
            displayStats()
            exit()

    except Exception as e:
        print (e)
        pass


def updateBad(actorfiles):                                # Mark bad images from "\bad images"

    try:
        badfolder = "bad images\\"   
        listOfFiles = os.listdir(badfolder)
        pattern = "*.jpg"
        for x in listOfFiles:                             #  Get bad folder list                 
            if fnmatch.fnmatch(x, pattern):
                actorfiles.append(x.split('.')[0] )       #  Remove file extension     
        #print(actorfiles)
        if len(actorfiles) == 0:
            print('There are no bad image files or user entries to process.') 
            return('bad')
        else:
            print('Bad file processing beginning.')
            db = openActorDB()
            for a in range(len(actorfiles)):
                matchfile = actorfiles[a]
                curp = db.execute('SELECT actorMatch FROM actorArtwork WHERE actorMatch=?', (matchfile,))
                actortuple = curp.fetchone() 
                if actortuple:
                    currDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')                
                    db.execute('UPDATE actorArtwork SET lastChecked=?, checkStatus=? WHERE actorMatch=?',  \
                    (currDateTime,'Bad Image', matchfile,))    
                    print('Actor image file marked bad: ' + matchfile) 
                else:
                    print('Actor image file not found in database: ' + matchfile) 

        del curp
        db.commit()
        db.close()
        return('good')

    except Exception as e:
        print (e)
        return('bad')
        pass

def getLast():                                      # Find last time checker ran

    try:
        global lastime
        db = openActorDB()
        curs = db.execute('select lastChecked FROM actorArtwork ORDER BY lastChecked \
        DESC LIMIT 1',)
        counttuple = curs.fetchone()
        if counttuple:
            lastime = str(counttuple[0])
        else:
            lastime = 'Never' 
        
        del curs, counttuple
        db.close()

    except Exception as e:
        print (e)
        pass


def displayStats():                                 # Display stats from Mezzmo Tracker DB

    try:
        global lasttime, tmdbact, imdbact, imdb_count, tmdb_count, sysarg1
        badcount = postfound = nopostmatch = upostfound = dactcount = 0
        actcount = mezcount = nomatch = noupostmatch = noart = 0

        db = openActorDB()        
        curs = db.execute('SELECT count (*) FROM userPosterFile',)
        counttuple = curs.fetchone()
        if counttuple:
            upostfound = str(counttuple[0])        
        curs = db.execute('SELECT count (*) FROM userPosterFile WHERE mezzmoMatch=? ',('No',))
        counttuple = curs.fetchone()   
        if counttuple:
            noupostmatch = str(counttuple[0])   
        curs = db.execute('SELECT count (*) FROM posterFile',)
        counttuple = curs.fetchone()
        if counttuple:
            postfound = str(counttuple[0])        
        curs = db.execute('SELECT count (*) FROM posterFile WHERE mezzmoMatch=? ',('No',))
        counttuple = curs.fetchone()   
        if counttuple:
            nopostmatch = str(counttuple[0])   
        curs = db.execute('select count (*) from actorArtwork where checkStatus=?',  \
        ('Bad Image',))
        counttuple = curs.fetchone()        
        if counttuple:
            badcount =  str(counttuple[0])
        curs = db.execute('select count (*) from actorArtwork where mezzmoChecked=?', ('Yes',))
        counttuple = curs.fetchone()        
        if counttuple:
            actcount =  str(counttuple[0])
        curs = db.execute('select count (*) from actorArtwork where mezzmoChecked=?', ('Deleted',))
        counttuple = curs.fetchone()        
        if counttuple:
            dactcount =  str(counttuple[0])
        curs = db.execute('select count (*) from actorArtwork where checkStatus=?',  \
        ('Found on Mezzmo',))
        counttuple = curs.fetchone()        
        if counttuple:
            mezcount =  str(counttuple[0])
        curs = db.execute('select count (*) from actorArtwork where posterFile IS    \
        NULL and userPosterFile IS NULL',)
        counttuple = curs.fetchone()
        if counttuple:
            nomatch =  str(counttuple[0])       
        curs = db.execute('select count (*) from actorArtwork where checkStatus LIKE \
        ?', ('No artwork%',))
        counttuple = curs.fetchone()        
        if counttuple:
            noart =  str(counttuple[0])

        if sysarg1 == 'images':
            print ("\nTMDB image queries: \t\t\t" + str(tmdb_count))
            print ("TMDB images found on this query: \t" + str(tmdbact))
            print ("IMDB image queries: \t\t\t" + str(imdb_count))
            print ("IMDB images found on this query: \t" + str(imdbact))
        print ('\n\t ************  Mezzmo Artwork Checker Stats  *************\n')
        print ("Last time checker ran: \t\t\t" + lastime)  
        print ("Mezzmo actors found: \t\t\t" + actcount)
        print ("Mezzmo actors deleted: \t\t\t" + dactcount)
        print ("Mezzmo Poster files found: \t\t" + postfound)
        print ("Mezzmo Poster files without actor: \t" + nopostmatch)
        print ("Mezzmo UserPoster files found: \t\t" + upostfound)
        print ("Mezzmo UserPoster files without actor: \t" + noupostmatch) 
        print ("Mezzmo actors with Good Image:  \t" + mezcount)   
        print ("Mezzmo actors with Bad Image:  \t\t" + badcount)
        print ("Mezzmo actors with no Image:   \t\t" + nomatch)
        print ("Mezzmo actors with no Image found:   \t" + noart)  

        del curs, counttuple
        db.close()

    except Exception as e:
        print (e)
        pass


def checkFolders():				    #  check initial folder structures

    try:
        if not os.path.exists('bad images'):        #  Check bad files location
            os.makedirs('bad images')
        if not os.path.exists('imdb'):              #  Check IMDB files location
            os.makedirs('imdb')
        if not os.path.exists('tmdb'):              #  Check TMDB files location
            os.makedirs('tmdb')

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
checkFolders()
checkClean(sysarg1, sysarg2)
checkBad()
getConfig()
getLast()
checkDatabase()
optimizeDB()
getMezzmo(mezzmodbfile)
getUserPosters(mezzmoposterpath)
getPosters(mezzmoposterpath)
getTMDBimages()
getIMDBimages()
checkCsv(csvout)
print('Mezzmo actor comparison completed successfully.')
displayStats()


