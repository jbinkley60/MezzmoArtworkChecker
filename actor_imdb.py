# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json
from datetime import datetime
import urllib.request, urllib.parse, urllib.error
import http.client
import mimetypes
from urllib.request import Request, urlopen
from common import genLog

version = 'version 1.0.20'
baseurl = 'https://tv-api.com/en/API/SearchName/'

def getImage(imdb_key, actorname, cstatus, image_size):         

    try:  
        actor = actorFile(actorname)                        #  Modify for UserPoster file naming
        outfile = 'imdb\\' + actor + '.jpg'

        if os.path.exists(outfile):                         #  Do not over write existing file.
            mgenlog = 'Skipping IMDB fetch.  Image already found in IMDB folder: ' + actorname
            genLog(mgenlog, 'Yes')
            return('imdb_found')   
        if cstatus != None and 'Bad' in cstatus:
            mgenlog = 'Skipping IMDB fetch.  Image file marked bad: ' + actorname
            genLog(mgenlog, 'Yes')
            return('imdb_bad')
        if cstatus != None and 'Found on Mezzmo' in cstatus:
            mgenlog = 'Skipping IMDB fetch.  Image already file on Mezzmo: ' + actorname
            genLog(mgenlog, 'Yes')
            return('imdb_mezzmo')
        if cstatus != None and 'Found at TMDB' in cstatus:
            mgenlog = 'Skipping IMDB fetch.  Image already found on TMDB: ' + actorname
            genLog(mgenlog, 'Yes')
            return('tmdb_found')
 
        #print (imdb_key)
        if 'Your' in imdb_key:
            return('imdb_badkey')      

        #print(actorname)
        if image_size == 'w500':
            imagepath = 'https://tv-api.com/API/ResizeImage?apiKey=' + imdb_key + '&size=500x750&url='
        elif image_size == 'w780':
            imagepath = 'https://tv-api.com/API/ResizeImage?apiKey=' + imdb_key + '&size=780x1170&url='
        else:
            imagepath = 'https://tv-api.com/API/ResizeImage?apiKey=' + imdb_key + '&size=300x450&url='

        conn = http.client.HTTPSConnection("tv-api.com", 443)
        headers = {'User-Agent': 'Mezzmo Artwork Checker 1.0.20'}
        req = '/en/API/SearchName/' + imdb_key + '/' + actorname
        reqnew = urllib.parse.quote(req)
        encoded = urllib.parse.urlencode(headers)
        #print(req)
        conn.request("GET", reqnew, encoded)        
        res = conn.getresponse()
        data = res.read()
        #print(data.decode('utf-8'))

        jdata = json.loads(data)
        error = jdata['errorMessage']                     #  Check for IMDB errors
        results = jdata['results']
        if len(error) > 0 and 'Invalid API Key' in error:
            #mgenlog = str(error)
            #print(mgenlog)
            #genLog(mgenlog)
            return('imdb_badkey')
        if len(error) > 0 and 'Server busy' in error:
            #mgenlog = str(error)
            #print(mgenlog)
            #genLog(mgenlog)
            return('imdb_busy')
        elif len(error) > 0:
            #mgenlog = str(error)
            #print(mgenlog)
            #genLog(mgenlog)
            return('imdb_error')

        if len(results) == 0:
            return('imdb_notfound')

        match = actormatch = counter = 0
        while match == 0 and counter < len(jdata['results']):         
            imdbname = (jdata['results'][counter]['title'])
            imdbrole = (jdata['results'][counter]['description'])
            profile_path = (jdata['results'][counter]['image'])
            #print(imdbname)
            #print(imdbrole)
            #print(profile_path)
            #print(counter)
            #print(len(jdata['results']))
            if imdbname == actorname:
                #print('Name match')
                if 'Actor' in imdbrole or 'Actress' in imdbrole or 'Self' in imdbrole or 'Stunts' in imdbrole   \
                or 'Additional Crew' in imdbrole:                
                    actormatch += 1
                    #print ('Actor match: ' + str(actormatch))
                    if profile_path and 'nopicture' not in profile_path:
                        imagefile = imagepath + profile_path
                        #print(imagefile)

                        req = Request(imagefile, headers={'User-Agent': 'Mezzmo Artwork Checker 1.0.19'})
                        data = urlopen(req).read()
                        output = open(outfile,"wb")
                        output.write(data)
                        output.close()
                        mgenlog = 'IMDB image found for: ' + actorname
                        genLog(mgenlog, 'Yes')
                        return('imdb_found')
                    else:    
                        counter += 1
                else:
                    counter += 1                     
            else:
                counter += 1

        if actormatch == 0:
            return('imdb_notfound')
        if match == 0:
            print('IMDB image not found for: ' + actorname)
            return('imdb_nopicture')

    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting the IMDB poster image for: ' + actorname
        print(mgenlog)
        genLog(mgenlog)
        return('imdb_error')
        pass


def actorFile(actorname):                      #  Modify the actor name to match UserPoster file naming

    try:
        pactor = actorname.lower().replace(' ', '-').replace('.','-').replace('&','-').replace("'",'-')
        actor = pactor.replace("(",'-').replace(')','-').replace('"','-').replace(',','')

        return(actor)

    except Exception as e:
        print (e)
        pass

