# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json
from datetime import datetime
import urllib.request, urllib.parse, urllib.error
from common import genLog

version = 'version 1.0.22'
base_url = 'https://api.themoviedb.org/3/search/person?'
#image_size = 'w300'
#image_size = 'w500'
#image_size = 'w780'

def getImage(tmdb_key, actorname, cstatus, image_size):     

    try:
        #global image_size

        actor = actorFile(actorname)                        #  Modify for UserPoster file naming
        if cstatus != None and 'search' in cstatus:
            outfile = 'UserPoster\\' + actor + '.jpg'
        else:
            outfile = 'tmdb\\' + actor + '.jpg'

        if os.path.exists(outfile):                         #  Do not over write existing file.
            mgenlog = 'Skipping TMDB fetch.  Image already found in TMDB folder: ' + actorname
            genLog(mgenlog, 'Yes')
            return('tmdb_skip')  
        if cstatus != None and 'Bad' in cstatus:
            mgenlog = 'Skipping TMDB fetch.  Image file marked bad: ' + actorname
            genLog(mgenlog, 'Yes')
            return('tmdb_bad')
        if cstatus != None and 'Found on Mezzmo' in cstatus:
            mgenlog = 'Skipping TMDB fetch.  Image already file on Mezzmo: ' + actorname
            genLog(mgenlog, 'Yes')
            return('tmdb_mezzmo')
        if cstatus != None and 'Found at IMDB' in cstatus:
            mgenlog = 'Skipping TMDB fetch.  Image already found on IMDB: ' + actorname
            genLog(mgenlog, 'Yes')
            return('tmdb_skip')

        if tmdb_key == None or len(tmdb_key) != 32:
            mgenlog = 'The TMDB key appears to be invalid. Please check.'
            print(mgenlog, "Yes")
            return('tmdb_badkey')

        headers = {'User-Agent': 'Mezzmo Artwork Checker 1.0.22'}
        hencoded = urllib.parse.urlencode(headers)

        parms = {'api_key': tmdb_key,                      #  TMDB URL Parms
                'language': 'en-US',                        
                'query': actorname,
                'page': '1',
                'include_adult': 'false',
                }

        queryInfo = urllib.parse.urlencode(parms)
        reqnew = urllib.parse.quote(base_url, safe=':/?')
        request = reqnew + queryInfo

        #imagepath = 'https://image.tmdb.org/t/p/original'
        imagepath = 'https://image.tmdb.org/t/p/' + image_size

        req = urllib.request.Request(request, headers=headers)
        jresponse = urllib.request.urlopen(req)
        jdata = json.load(jresponse)

        match = actormatch = counter = 0
        while match == 0 and counter < len(jdata['results']):         
            tmdbname = (jdata['results'][counter]['name'])
            if 'known_for_department' in jdata['results'][counter].keys():
                tmdbrole = (jdata['results'][counter]['known_for_department'])
                #print(tmdbrole)
            else:
                tmdbrole = None
            profile_path = (jdata['results'][counter]['profile_path'])
            #print(tmdbname)
            #print(counter)
            #print(len(jdata['results']))
            if tmdbname == actorname:
                #print('Name match')
                if tmdbrole != None and tmdbrole == 'Acting':                
                    actormatch += 1
                    #print (actormatch)
                    if profile_path:
                        imagefile = imagepath + profile_path
                        #print(imagefile)
                        resource = urllib.request.urlopen(imagefile)
                        output = open(outfile,"wb")
                        output.write(resource.read())
                        output.close()
                        mgenlog = 'TMDB image found for: ' + actorname
                        genLog(mgenlog, 'Yes')
                        return('tmdb_found')
                    else:    
                        counter += 1
                else:
                    counter += 1                     
            else:
                counter += 1

        if actormatch == 0:
            return('tmdb_notfound')
        if match == 0:
            print('TMDB image not found for: ' + actorname)
            return('tmdb_nopicture')

    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting the TMDB poster image for: ' + actorname
        print(mgenlog)
        genLog(mgenlog)
        return('tmdb_notfound')
        pass


def actorFile(actorname):                      #  Modify the actor name to match UserPoster file naming

    try:
        pactor = actorname.lower().replace(' ', '-').replace('.','-').replace('&','-').replace("'",'-')
        actor = pactor.replace("(",'-').replace(')','-').replace('"','-').replace(',','')

        return(actor)

    except Exception as e:
        print (e)
        pass


