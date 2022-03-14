# -*- coding: utf-8 -*-
# #!/usr/bin/python
import os, fnmatch, sys, csv, json
from datetime import datetime
import urllib.request, urllib.parse, urllib.error
import http.client
import mimetypes
from urllib.request import Request, urlopen

version = 'version 1.0.3'
baseurl = 'https://imdb-api.com/en/API/SearchName/'


if not os.path.exists('imdb'):
    os.makedirs('imdb')

def getImage(imdb_key, actorname):         

    try:  
        #print (imdb_key)
        if 'Your' in imdb_key:
            print('\n===========================================================')
            print('Please enter a valid IMDB API Key in the configuration file.')
            print('You can get IMDB API keys at: https://imdb-api.com/pricing')
            print('A free IMDB API key will allow up to 100 images a day.')
            print('===========================================================\n')
            return('error') 
        pactor = actorname.lower().replace(' ', '-').replace('.','-').replace('&','-').replace("'",'-')
        actor = pactor.replace("(",'-').replace(')','-').replace('"','-').replace(',','')
        outfile = 'imdb\\' + actor + '.jpg'
        uname = actorname.replace(' ','%20')

        imagepath = 'https://imdb-api.com/images/262x360/'

        conn = http.client.HTTPSConnection("imdb-api.com", 443)
        payload = ''
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) \
        Gecko/20100101 Firefox/98.0'}
        req = '/en/API/SearchName/' + imdb_key + '/' + uname
        #print(req)
        conn.request("GET", req, payload, headers)
        res = conn.getresponse()
        data = res.read()
        #print(data.decode('utf-8'))

        jdata = json.loads(data)
        error = jdata['errorMessage']                    #  Check for IMDB error
        if len(error) > 0:
            print(error)
            return('error')

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
                return('found')
                #break
            else:
                print('IMDB image not found for: ' + actorname)
                return('nopicture')

        else:
            print ('Image not available')


    except Exception as e:
        print (e)
        pass

#getImage(api_key, name)

