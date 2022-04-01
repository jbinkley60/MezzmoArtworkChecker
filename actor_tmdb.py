# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json
from datetime import datetime
import urllib.request, urllib.parse, urllib.error

version = 'version 1.0.7'
base_url = 'https://api.themoviedb.org/3/search/person?'
image_size = 'w300'

def getImage(tmdb_key, actorname, cstatus):     

    try:
        global image_size

        actor = actorFile(actorname)                        #  Modify for UserPoster file naming
        outfile = 'tmdb\\' + actor + '.jpg'

        if os.path.exists(outfile):                         #  Do not over write existing file.
            print('Skipping TMDB fetch.  Image already found in TMDB folder: ' + actorname)
            return('tmdb_found')  
        if cstatus != None and 'Bad' in cstatus:
            print('Skipping TMDB fetch.  Image file marked bad: ' + actorname)
            return('tmdb_bad')
        if cstatus != None and 'Found on Mezzmo' in cstatus:
            print('Skipping TMDB fetch.  Image already file on Mezzmo: ' + actorname)
            return('tmdb_mezzmo')
        if cstatus != None and 'Found at IMDB' in cstatus:
            print('Skipping TMDB fetch.  Image already found on IMDB: ' + actorname)
            return('tmdb_found')

        if tmdb_key == None or len(tmdb_key) != 32:
            return('tmdb_badkey')

        headers = {'User-Agent': 'Mezzmo Artwork Checker 1.0.7'}
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
            tmdbrole = (jdata['results'][counter]['known_for_department'])
            profile_path = (jdata['results'][counter]['profile_path'])
            #print(tmdbname)
            #print(tmdbrole)
            #print(counter)
            #print(len(jdata['results']))
            if tmdbname == actorname:
                #print('Name match')
                if tmdbrole == 'Acting':                
                    actormatch += 1
                    #print (actormatch)
                    if profile_path:
                        imagefile = imagepath + profile_path
                        #print(imagefile)
                        resource = urllib.request.urlopen(imagefile)
                        output = open(outfile,"wb")
                        output.write(resource.read())
                        output.close()
                        print('TMDB image found for: ' + actorname)
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
        #print (e)
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


