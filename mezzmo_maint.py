# -*- coding: utf-8 -*-
# #!/usr/bin/python
import json, os, io, sys, pickle, shutil
from datetime import datetime
from common import genLog, openActorDB, openMezzmoDB
from pathlib import Path
import time
import pandas as pd

def mezzmomaintmenu(ac_config):                               # Mezzmo maintenance menu

        mezzrunning = checkMezzmo(ac_config)
        mezzmopath = ac_config['mezzmopath']
        while mezzrunning == 0:
            os.system('cls')
            print('Mezzmo running detected.  You will need to shutdown Mezzmo to continue.')
            choicem = input('\nHave you shtudown Mezzmo (Y/N) or Enter X to Exit:  ')
            if choicem.lower() == 'x':
                return
            mezzrunning = checkMezzmo(ac_config)         

        choice = '-1'
        mezzconn = ac_config['mezzconn']
        while choice.lower() not in ['0', 'x']:
            os.system('cls')
            print('\t\tMezzmo Database Maintenance Utilities\n')
            print(' 1.  Manual Mezzmo Database file backup (not artwork)')
            print(' 2.  Reindex Mezzmo Database to Improve Performance')
            print(' 3.  Compact Mezzmo datatasbe to Reduce Space')      
            print(' 4.  Future')
            print(' 5.  Export Mezzmo Actor table')
            print(' 6.  Export Mezzmo file table ')
            print(' 7.  Esport Mezzmo folders table')
            print(' 8.  Export Mezzmo playlists table ')
            print(' 9.  Duplicate Movies Report')
            print('10.  Duplicate TV Show Episode Report\n\n ')
            choice = input(' Enter Mezzno Maintenance command (or X to Exit) ? ')

            if choice.lower() == 'x':
                mgenlog = 'User chose to exit out of Mezzmo maintenance functions.'
                genLog(mgenlog)
                return
            elif choice == '1':                              
                makeMezzmoBackups(ac_config)
            elif choice == '2':
                mezzmoDButils(mezzmopath, mezzconn, 'reindex')
            elif choice == '3':
                mezzmoDButils(mezzmopath, mezzconn, 'compact')
            elif choice == '5':
                exportMezzmo(mezzconn, 'actor')
            elif choice == '6':
                exportMezzmo(mezzconn, 'file')
            elif choice == '7':
                exportMezzmo(mezzconn, 'folder')
            elif choice == '8':
                exportMezzmo(mezzconn, 'playlist')               
            elif choice == '9':
                exportMezzmo(mezzconn, 'mvdupes')
            elif choice == '10':
                exportMezzmo(mezzconn, 'epdupes')


def mezzmoresponse(ac_config):                                # Check Mezzmo running

            mezzmopath = ac_config['mezzmopath']
            mezzrunning = os.path.isfile(mezzmopath + 'mezzmo.db-wal')
            print('Is Mezzmo running: ' + str(mezzrunning))
            returnval = ''
            if os.path.exists('state_save.pkl'):
                with open("state_save.pkl", "rb") as f:
                    state_save = pickle.load(f)
                f.close()
                #print('Saved state: ' + str(state_save))

            if state_save['mezzmo_reminder'] in ['', 'n']:
                mezzmo_on = input('Have you checked to ensure the Mezzmo service and GUI are not running (Y/N) ?  ')
                if mezzmo_on.lower() != 'y':
                    mgenlog = 'User did not confirm Mezzmo shutdown.  Aborting direct Mezzmo DB updates.'
                    genLog(mgenlog)
                    returnval = 0
                else:
                    returnval = 1
                state_save['mezzmo_reminder'] = mezzmo_on.lower()
            else:
                returnval = 1

            with open("state_save.pkl", "wb") as f:
                pickle.dump(state_save, f)
            f.close()
            return returnval


def checkMezzmo(ac_config):                                 # Check if Mezzmo is running

        mezzmopath = ac_config['mezzmopath']
        mezzwal = os.path.isfile(mezzmopath + 'mezzmo.db-wal')
        mezzshm = os.path.isfile(mezzmopath + 'mezzmo.db-shm')

        if mezzwal or mezzshm:
            return 0
        else:
            return 1


def backupresponse(ac_config):                                          # Check Backup response

            returnval = ''
            if os.path.exists('state_save.pkl'):
                with open("state_save.pkl", "rb") as f:
                    state_save = pickle.load(f)
                f.close()
                #print('Saved state: ' + str(state_save))

            if state_save['backup_reminder'] == '':
                bkup = input('Would you like to backup your Mezzmo database before making updates (Y/N) ? ' )
                if 'y' in bkup:
                    mgenlog = 'User chose to perform Mezzmo backup. '
                    genLog(mgenlog)
                    makeMezzmoBackups(ac_config)
                    backup_reminder = bkup.lower()
                state_save['backup_reminder'] = bkup.lower()

            with open("state_save.pkl", "wb") as f:
                pickle.dump(state_save, f)
            f.close()
            return returnval


def makeMezzmoBackups(ac_config):                                              # Make Mezzmo database backups

    try:
        os.system('cls')
        starttime = time.time()
        mezzmopath = ac_config['mezzmopath']                                   # Path the Mezzmo database
        mezzconn = ac_config['mezzconn']                                       # DB connection WAL or Journal mode
        mezzbackups = ac_config['mezzbackups']                                 # NUmber of backups to keep
        mezzdisksp = ac_config['mezzdisksp']                                   # Minimum disk space

        backup_path = mezzmopath  + '\\artwork_checker_backups'

        #print(backup_path)
        print('\n')
        if not os.path.exists(backup_path):                                    # Check if backup folder exists
            os.makedirs(backup_path)   #  check Mezzmo database backfup folder

        if checkBackupLimits(backup_path, mezzbackups, mezzdisksp) == 0:       # Check numbers of backup and disk space
            input('Hit Enter to Continue')
            return

        try:
            from sqlite3 import dbapi2 as sqlite
        except:
            from pysqlite2 import dbapi2 as sqlite    
        #sys.exit()
        DB = backup_path + '\\mezzmo_' + datetime.now().strftime('%m%d%Y-%H%M%S') + '.db'
        dbout = sqlite.connect(DB)
        dbin = openMezzmoDB(mezzconn)

        mgenlog = 'Mezzmo database backup beginning.  Be patient. This could take a few minutes to complete.'
        genLog(mgenlog, 'yes') 

        with dbout:
            dbin.backup(dbout, pages=25000)
        dbout.close()
        dbin.close()
        mgenlog = 'Mezzmo database backup successful: ' + str(DB)
        genLog(mgenlog, 'yes')
        endtime = time.time()
        duration = endtime-starttime
        difference = str(int(duration // 60)) + 'm ' + str(int(duration % 60)) + 's'
        mgenlog = 'Mezzmo database backup duration: ' + difference
        genLog(mgenlog, 'yes')
        input('\nHit enter to continue')

    except Exception as e:
        #print (e)
        mgenlog = 'An error occurred creating a Mezzmo database backup. ' + str(e)
        genLog(mgenlog, 'yes')
        dbin.close()


def checkBackupLimits(backup_path, mezzbackups, mezzdisksp):                   # Check maximum limits

        paths = sorted(Path(backup_path).iterdir(), key=os.path.getmtime, reverse=True)
        #print(str(paths))
        backup_files = []
        for path in paths:
            if 'mezzmo_' in str(path):
                backup_files.append(str(path))
        if int(mezzbackups) == 0:
            mgenlog = 'Mezzmo backup file retention set to unlimited. Bakup files found: ' + str(len(backup_files))
            genLog(mgenlog, 'yes')
        elif len(backup_files) <= int(mezzbackups):
            mgenlog = 'Mezzmo backup file count: ' +  str(len(backup_files)) + ' is less than maximum retention setting: ' + str(mezzbackups)
            genLog(mgenlog, 'yes')
        else:
            startpos = len(backup_files) - (len(backup_files) - int(mezzbackups))
            for backup in backup_files[startpos:]:                             # Delete extra backups
                #print('File to delete: ' + str(backup))
                command = 'del ' + str(backup) + ' /q >nul 2>nul'              #  Remove old backup files
                os.system(command)                
                mgenlog = 'Mezzmo older database backup file deleted: ' + str(backup)
                genLog(mgenlog, 'yes')                                              

        total, used, free = shutil.disk_usage(backup_path)
        free_space = int(free / (2**30))
        free_space_text = str(free_space) + ' GB'
        #print('\n')
        if int(mezzdisksp) < free_space:
            mgenlog = 'Mezzmo backup sufficient space available: ' + free_space_text
            genLog(mgenlog, 'yes')
            return 1
        else:
            mgenlog = 'Mezzmo backup insufficient space available: ' + free_space_text
            genLog(mgenlog, 'yes')
            return 0
        

def mezzmoDButils(mezzmopath, mezzconn, option):               # Mezzmo database utilities

        starttime = time.time()
        db = openMezzmoDB(mezzconn)
        if option == 'reindex':
            print('\n')
            mgenlog = 'Mezzmo database reindexing beginning.  Be patient.  This could take a few minutes to complete.'
            genLog(mgenlog, 'yes')
            db.execute('REINDEX',)
            mgenlog = 'Mezzmo database reindexing successful'
            genLog(mgenlog, 'yes')
            endtime = time.time()
            duration = endtime-starttime
            difference = str(int(duration // 60)) + 'm ' + str(int(duration % 60)) + 's'
            mgenlog = 'Mezzmo database reindexing duration: ' + difference
            genLog(mgenlog, 'yes')
        elif option == 'compact':
            print('\n')
            mgenlog = 'Mezzmo database compacting beginning.  Be patient.  This could take a few minutes to complete.'
            genLog(mgenlog, 'yes')
            db.execute('VACUUM',)
            mgenlog = 'Mezzmo database compacting successful'
            genLog(mgenlog, 'yes')
            endtime = time.time()
            duration = endtime-starttime
            difference = str(int(duration // 60)) + 'm ' + str(int(duration % 60)) + 's'
            mgenlog = 'Mezzmo database compacting duration: ' + difference
            genLog(mgenlog, 'yes')

        db.close()
        input('\nHit enter to continue')


def exportMezzmo(mezzconn, option):                            #  Export various Mezzmo data to XLS files

        outtime = datetime.now().strftime('%m%d%Y-%H%M%S')

        db = openMezzmoDB(mezzconn)

        if option == 'actor':
            outfile = 'reports\\Mezzmo MGOFileArtist Table Export_' + outtime + '.xlsx'
            print('\n')
            mgenlog = 'Beginning Mezzmo FileArtist table export'
            genLog(mgenlog, 'yes')
            dbcurr = db.execute('SELECT * FROM MGOFileArtist')
            dbtuples = dbcurr.fetchall()
            headers = [i[0] for i in dbcurr.description]
            del dbcurr
            mgenlog = 'Mezzmo MGOFileArtist Table export successful: ' + outfile
        elif option == 'file':
            outfile = 'reports\\Mezzmo MGOFile Table Export_' + outtime + '.xlsx'
            print('\n')
            mgenlog = 'Beginning Mezzmo File table export'
            genLog(mgenlog, 'yes')
            dbcurr = db.execute('SELECT * FROM MGOFile')
            dbtuples = dbcurr.fetchall()
            headers = [i[0] for i in dbcurr.description]
            del dbcurr
            mgenlog = 'Mezzmo MGOFile Table export successful: ' + outfile
        elif option == 'folder':
            outfile = 'reports\\Mezzmo MGOSubWatchFolder Table Export_' + outtime + '.xlsx'
            print('\n')
            mgenlog = 'Beginning MGOSubWatchFolder Table export'
            genLog(mgenlog, 'yes')
            dbcurr = db.execute('SELECT * FROM MGOSubWatchFolder')
            dbtuples = dbcurr.fetchall()
            headers = [i[0] for i in dbcurr.description]
            del dbcurr
            mgenlog = 'Mezzmo MGOSubWatchFolder Table export successful: ' + outfile
        elif option == 'playlist':
            outfile = 'reports\\Mezzmo MGOPlaylist Table Export_' + outtime + '.xlsx'
            print('\n')
            mgenlog = 'Beginning MGOPlaylist Table export'
            genLog(mgenlog, 'yes')
            dbcurr = db.execute('SELECT * FROM MGOPlaylist')
            dbtuples = dbcurr.fetchall()
            headers = [i[0] for i in dbcurr.description]
            del dbcurr
            mgenlog = 'Mezzmo MGOPlaylist Table export successful: ' + outfile
        elif option == 'mvdupes':
            outfile = 'reports\\Mezzmo Duplicate Movie Report_' + outtime + '.xlsx'
            dbcurr = db.execute('select MGOFile.Title as Title, MGOFile.Year as Year, MGOFile.File  \
            as File from MGOFile where disc = 0 and TypeUID = 4 group by Title having count (*) > 1')
            dbtuples = dbcurr.fetchall()
            headers = [i[0] for i in dbcurr.description]
            del dbcurr
            mgenlog = 'Mezzmo Duplicate Movie Report successful: ' + outfile
        elif option == 'epdupes':
            outfile = 'reports\\Mezzmo Duplicate Episodes Report_' + outtime + '.xlsx'
            dbcurr = db.execute('select MGOFileAlbum.Data as Series, MGOFile.Disc as Season,         \
            MGOFile.Track as Episode, MGOFile.File from MGOFile                                      \
            inner join MGOFileAlbumRelationship on MGOFile.ID = MGOFileAlbumRelationship.FileID      \
            inner join MGOFileAlbum on MGOFileAlbumRelationship.ID = MGOFileAlbum.ID                 \
            where disc > 0 and TypeUID = 4 group by series, season, episode having count (*) > 1')        
            dbtuples = dbcurr.fetchall()
            headers = [i[0] for i in dbcurr.description]
            del dbcurr
            mgenlog = 'Mezzmo Duplicate Episodes Report successful: ' + outfile

        
        db.close()

        if len(dbtuples)  == 0:
            print('\n')
            mgenlog = 'No matching records found in Mezzmo database'
        else:  
            df = pd.DataFrame(dbtuples, columns = headers)
            df.to_excel(outfile, index=False)
        print('\n')
        genLog(mgenlog, 'yes')       
        input('\nHit enter to continue')




