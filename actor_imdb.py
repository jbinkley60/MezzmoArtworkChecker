# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json
from datetime import datetime
import urllib.request, urllib.parse, urllib.error
import http.client
import mimetypes
from urllib.request import Request, urlopen

version = 'version 1.0.4'
baseurl = 'https://imdb-api.com/en/API/SearchName/'


if not os.path.exists('imdb'):
    os.makedirs('imdb')

def getImage(imdb_key, actorname, cstatus):         

    try:  
        if cstatus != None and 'Bad' in cstatus:
            print('Skipping IMDB fetch.  Image file marked bad: ' + actorname)
            return('imdb_bad')
        if cstatus != None and 'Found on Mezzmo' in cstatus:
            print('Skipping IMDB fetch.  Image already file on Mezzmo: ' + actorname)
            return('imdb_mezzmo')
        if cstatus != None and 'Found at IMDB' in cstatus:
            print('Skipping IMDB fetch.  Image already found on IMDB: ' + actorname)
            return('imdb_found')
 
        #print (imdb_key)
        if 'Your' in imdb_key:
            print('\n===========================================================')
            print('Please enter a valid IMDB API Key in the configuration file.')
            print('You can get IMDB API keys at: https://imdb-api.com/pricing')
            print('A free IMDB API key will allow up to 100 images a day.')
            print('===========================================================\n')
            return('imdb_badkey') 
        actor = actorFile(actorname)                        #  Modify for UserPoster file naming
        outfile = 'imdb\\' + actor + '.jpg'
        #print(actorname)
        imagepath = 'https://imdb-api.com/images/262x360/'

        conn = http.client.HTTPSConnection("imdb-api.com", 443)
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) \
        #Gecko/20100101 Firefox/98.0'}
        headers = {'User-Agent': 'Mezzmo Artwork Checker 1.04'}
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
            print(error)
            return('imdb_badkey')
        if len(error) > 0 and 'Server busy' in error:
            print(error)
            return('imdb_busy')
        elif len(error) > 0:
            print(error)
            return('imdb_error')

        if len(results) == 0:
            return('imdb_notfound')

        for a in range(len(jdata['results'])):
            profile_path = (jdata['results'][a]['image'])
            title = (jdata['results'][a]['title'])
            description = (jdata['results'][a]['description'])

            #print(profile_path)
            #print(title)
            #print(description)

            if profile_path and title == actorname and 'nopicture' not in profile_path  \
            and ('Actor' in description or 'Actress' in description):
                rindex = profile_path.rfind('/')
                profile = profile_path[rindex+1:]
                imagefile = imagepath + profile
                #print(imagefile)

                req = Request(imagefile, headers={'User-Agent': 'Mozilla/5.0'})
                data = urlopen(req).read()
                output = open(outfile,"wb")
                output.write(data)
                output.close()
                print('IMDB image found for: ' + actorname)
                return('imdb_found')
                #break
            else:
                print('IMDB image not found for: ' + actorname)
                return('imdb_nopicture')

        else:
            print ('Image not available')


    except Exception as e:
        print (e)
        pass


def actorFile(actorname):                      #  Modify the actor name to match UserPoster file naming

    try:
        pactor = actorname.lower().replace(' ', '-').replace('.','-').replace('&','-').replace("'",'-')
        actor = pactor.replace("(",'-').replace(')','-').replace('"','-').replace(',','')

        return(actor)

    except Exception as e:
        print (e)
        pass

