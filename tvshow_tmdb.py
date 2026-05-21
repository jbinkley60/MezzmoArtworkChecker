# -*- coding: utf-8 -*-
# #!/usr/bin/python
import urllib.request, urllib.parse, urllib.error
import json, os, io, sys
import requests
from datetime import datetime
from common import genLog, openActorDB
from actor_tmdb import getImage, actorFile

base_url = 'https://api.themoviedb.org/3/search/tv?'
tvshow_url = 'https://api.themoviedb.org/3/tv/{}?'
ratings_url = 'https://api.themoviedb.org/3/tv/{}/content_ratings?'
poster_base = 'https://image.tmdb.org/t/p/w500'
backdrop_base = 'https://image.tmdb.org/t/p/original'
version_name = 'version v1.0.23'
version  = "1.0.23"
headers = {'User-Agent': 'Mezzmo Artwork Checker ' + version}
tmdb_key = ''
imgsize = "w300"
file = ''

def selectTVshow(key, imagesize):                   # Select TV Show from TMDB

    try:
        global tmdb_key, imgsize
        tmdb_key = key
        imgsize = imagesize

        tvshow = rel_year = ''
             
        tvshow = input(' Enter TV Show series title  (i.e. Happy Days) ?\n')
        rel_year = input(' Enter TV Show first year or hit enter to leave blank (i.e. 1977) ?\n')
        print('\n')
        mgenlog = 'NFO TV Show search on: ' + tvshow + ' ' + rel_year
        genLog(mgenlog)
        tvshowlist = getTVShowList(tmdb_key, tvshow, rel_year)

        if len(tvshowlist) == 0:
            mgenlog = 'No matching TV Shows found'
            print('\n No matching TV Shows found')
            #genLog(mgenlog, 'Yes')
            sys.exit()
        else:
            tvselection = getTvShowSelection(tvshowlist)
        if tvselection == 0:
            print('\n No TV show selected')

        else:
            tvshowdetails = getTVShowDetails(tmdb_key, tvselection)
        if tvshowdetails == 0:
            print(' No TV Show details received.')
        else:
            parseTvShowDetails(tvshowdetails)    

    except Exception as e:
        print (e)
        print(' There was an error getting the NFO menu')     
           

def getTVShowList(tmdb_key, tvshow, rel_year):

    try:
        tvshowlist = []
        hencoded = urllib.parse.urlencode(headers)

        parms = {'api_key': tmdb_key,                      #  TMDB URL Parms
                'language': 'en-US',
                'accept': 'application/json',
                'adult': False,
                'first_air_date_year': rel_year,                      
                'query': tvshow,
                }  

        queryInfo = urllib.parse.urlencode(parms)
        reqnew = urllib.parse.quote(base_url, safe=':/?')
        request = reqnew + queryInfo

        #print(request)

        jresponse = requests.get(request, headers=headers)
        #jresponse = urllib.request.urlopen(req)

        #print(jresponse.status_code)
        if int(jresponse.status_code) != 200:
            mgenlog = 'An error response code ' + str(jresponse.status_code) + ' was received from TMDB.'
            genLog(mgenlog, 'Yes')
            return tvshowlist
            
        jdata = jresponse.json()

        print(str(jdata))
        print('The number of TV Show matches is: ' + str(len(jdata)))      
 
        counter = 0
        while counter < len(jdata['results']) and counter < 10:
            currshow = {} 
            currshow['order'] = counter + 1    
            currshow['title'] = (jdata['results'][counter]['name'])
            currshow['year'] = (jdata['results'][counter]['first_air_date'][:4])
            currshow['tmdb_id'] = (jdata['results'][counter]['id'])
            currshow['overview'] = (jdata['results'][counter]['overview'])
            counter += 1
            #print(year[:4] + '\t' + title)
            tvshowlist.append(currshow)
            #print(str(counter))
            #print(str(currshow))
            del currshow
        #print(str(tvshowlist))
        return tvshowlist

    except Exception as e:
        print (e)
        print(' There was an error getting the TV Show ID')
        return tvshowlist 


def getTvShowSelection(tvshowlist):                    # Get Movie selection   

    try:
        global file
        os.system('cls')
        
        print('\n    Year\t\tTitle\t\t\t\t\t\tOverview\n')
        for x in range(len(tvshowlist)):
            if len(tvshowlist[x]['year']) < 4:
                year = '    '
            else:
                year = tvshowlist[x]['year']
            if x < 9:
                #print(' ' + str(tvshowlist[x]['order']) + '.  ' + year + '    '    \
                #+ tvshowlistx]['title'])
                print(' ' + str(tvshowlist[x]['order']) + '.  ' + year + '    '    \
                + "{:<48}".format(tvshowlist[x]['title'][:44]) + tvshowlist[x]['overview'][:70])

            else:
                print(' ' + str(tvshowlist[x]['order']) + '. ' + year + '    '    \
                + tvshowlist[x]['title']) 

        choice = -2
        while choice != -1 or choice > len(tvshowlist) - 1:
            choice = input('\n Enter number of TV Show to get details or 0 to exit ?\n')
            if len(choice) > 0 and str(choice).isdigit() and int(choice) != 0:     # Vaild entry
                choice = int(choice) - 1
            elif len(choice) == 0 or str(choice).isdigit() and int(choice) == 0:   # User exit
                mgenlog = 'User requested to exit.'
                genLog(mgenlog, 'Yes')
                sys.exit()
            if not str(choice).isdigit() or choice > len(tvshowlist) - 1:           # Invalid entry
                print(' Invalid entry.  Please select a movie number')
                choice = -2
            elif choice > -1 and choice < len(tvshowlist):                          # Valid entry
                mgenlog = 'User selected ' + str(choice + 1) + ' - ' + tvshowlist[choice]['title']
                genLog(mgenlog)
                break

        print ('\n Hit enter to use TV Show title as the NFO name or enter a new file ')
        choice2 = input(' name to use.  (i.e. Happy Days 1974)  ?\n')
        if len(choice2) > 0:
            file = choice2
            mgenlog = 'User entered custom NFO file name: ' + choice2
            genLog(mgenlog)
        return tvshowlist[choice]          


    except Exception as e:
        print (e)
        mgenlog = ' There was an error getting the TV Show selection'
        genLog(mgenlog, 'Yes')
        return 0 


def getTVShowDetails(tmdb_key, tvselection):                    # Get Movie details   

    try:
        os.system('cls')
        #print(str(tvselection))

        tmdb_id = tvselection['tmdb_id']
        details_url = tvshow_url.format(tmdb_id)

        hencoded = urllib.parse.urlencode(headers)

        parms = {'api_key': tmdb_key,                             #  TMDB URL Parms
                'language': 'en-US',
                'accept': 'application/json',
                'adult': False,                    
                'append_to_response': 'casts,trailers,releases',
                }  

        queryInfo = urllib.parse.urlencode(parms)
        reqnew = urllib.parse.quote(details_url, safe=':/?')
        request = reqnew + queryInfo

        #print(request)

        jresponse = requests.get(request, headers=headers)
        mdata = jresponse.json()

        #print(str(mdata))
        return(mdata)


    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting the TV Show details'
        genLog(mgenlog, 'Yes')
        return 0


def parseTvShowDetails(mdata):                                   # Parse JSON movie details data

    try:
        global file
        # print(mdata.keys())
        if 'name' in mdata.keys():
            if len(file) > 0:                                   # Use file name from user
                title = file
            else:
                title = mdata['name']
            # print(title)
        if 'id' in mdata.keys():
            id = str(mdata['id'])
        else:
            id = None
            #print(mdata['id'])
        if 'imdb_id' in mdata.keys():
            imdb_id = mdata['imdb_id']
        else:
            imdb_id = None
            #print(mdata['imdb_id'])
        if 'tagline' in mdata.keys() and len(mdata['tagline']) > 0:
            tagline = mdata['tagline']
            #print(mdata['tagline'])
        else:
            tagline = None   
        if 'homepage' in mdata.keys() and len(mdata['homepage']) > 0:
            homepage = mdata['homepage']
            #print(mdata['homepage'])
        else:
            homepage = None
        if 'first_air_date' in mdata.keys():
            release_date = mdata['first_air_date']
            release_year = mdata['first_air_date'][:4]
            #print(mdata['first_air_date])
            #print(mdata['first_air_date'][:4])
        else:
            release_date = None
            release_year = None
        if 'vote_average' in mdata.keys():
            vote_average = mdata['vote_average']
            #print(str(mdata['vote_average']))
        else:
            vote_average = None
        if 'belongs_to_collection' in mdata.keys() and mdata['belongs_to_collection'] != None:
            collection = mdata['belongs_to_collection']['name']
            #print(str(mdata['belongs_to_collection']['name']))
        else:
            collection = None
        if 'overview' in mdata.keys() and len(mdata['overview']) > 0:
            overview = mdata['overview']
            #print(str(mdata['overview']))
        else:
            overview = None
        if 'genres' in mdata.keys():
            genres = mdata.get('genres')
            genrelist = []
            for genre in range(len(genres)):
                genrelist.append(genres[genre]['name']) 
            #print(str(genrelist))
        else:
            genrelist = None          
        if 'releases' in mdata.keys():
            mpaa = 'NR'
            releases = mdata.get('releases')
            countries = releases.get('countries')
            for country in range(len(countries)):
                if 'iso_3166_1' in countries[country].keys():
                    if countries[country]['iso_3166_1'] == 'US':
                        mpaa = countries[country]['certification']
                        #print(mpaa)
                        break
        else:
            mpaa = None  
        if 'production_companies' in mdata.keys():
            production_companies = mdata.get('production_companies')
            studiolist = []
            for company in range(len(production_companies)):
                studiolist.append(production_companies[company]['name'])
            #print(str(studiolist))
        else:
            studiolist = None                             
        if 'casts' in mdata.keys():
            cast = mdata.get('casts')
            actors = cast.get('cast')
            actorlist = []
            #actcount = 0
            for actor in range(len(actors)):
                if actors[actor]['known_for_department'] == 'Acting':
                    actorlist.append(actors[actor]['name'])
                    #actorder = actors[actor]['order']
                    #actcount +=1
            #print(str(actorlist))
        else:
            actorlist = None
        if 'casts' in mdata.keys():
            crew = mdata.get('casts')
            crews = crew.get('crew')
            producerlist = []
            directorlist = []
            writerlist = []
            for crew in range(len(crews)):
                name = crews[crew]['name']
                department = crews[crew]['department']
                job = crews[crew]['job']
                if department.lower() in ['writing'] and job.lower() in       \
                ['writer', 'screenplay', 'short story']:
                    writerlist.append(name)
                elif department.lower() in ['production'] and job.lower() in       \
                ['producer']:
                    producerlist.append(name)
                elif department.lower() in ['directing'] and job.lower() in       \
                ['director']:
                    directorlist.append(name)
            #print('Writer list: ' + str(writerlist))  
            #print('Producer list: ' + str(producerlist))
            #print('Director list: ' + str(directorlist))
        else:
            writerlist = None
            producerlist = None
            directorlist = None               

        if 'trailers' in mdata.keys():
            videos = mdata.get('trailers')
            trailers = videos.get('youtube')
            trailerlist = []
            for trailer in trailers:
                if trailer['type'] == 'Trailer':
                    trailerlist.append('https://www.youtube.com/watch?v=' + trailer['source'])
                    #print('https://www.youtube.com/watch?v=' + trailer['source'])
        else:
            trailerlist = None

        title = title.replace(':', '-')                       # Eliminate invalid file name characters

        createNfoFile(title, id, imdb_id, tagline, homepage, release_date, mpaa, collection, overview, \
        genrelist, studiolist, writerlist, producerlist, directorlist, actorlist, trailerlist)
        getArtwork(title, mdata)
        createExtrasFile(title, id, vote_average, homepage, producerlist, actorlist, trailerlist)
        mgenlog = ' Mezzmo Artwork Checker NFO creation process completed.'
        genLog(mgenlog, 'Yes')       

    except Exception as e:
        print (e)
        print(' There was an error parsing the TV Show details')
        return 0


def createNfoFile(title, id, imdb_id, tagline, homepage, release_date, mpaa, collection, overview, \
    genrelist, studiolist, writerlist, producerlist, directorlist, actorlist, trailerlist): 

    try:
        nfofile = 'nfo\\' + title + '-series.xml'
        mgenlog = 'Target NFO file: ' + nfofile
        genLog(mgenlog)
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        #fileh = open(nfofile, "w")                                       #  Create NFO file
        with io.open(nfofile,'w',encoding='utf8') as fileh:
            fileh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility ' + version + ' -->\n\n')
            fileh.write('<series>\n')
            fileh.write('    <seriesname>' + title + '</seriesname>\n')
            if id != None:
                fileh.write('    <tmdbid>' + id + '</tmdbid>\n')

            if imdb_id != None:
                fileh.write('    <imdbid>' + imdb_id + '</imdbid>\n')
 
            if tagline != None:
                fileh.write('    <tagline>' + tagline + '</tagline>\n')

            #if homepage != None:
            #   fileh.write('    <homepage>' + homepage + '</homepage>\n')

            if release_date != None:
                fileh.write('    <premiered>' + release_date + '</premiered>\n')
                fileh.write('    <year>' + release_date[:4] + '</year>\n')

            #if vote_average != None:
            #    fileh.write('    <rating>' + str(vote_average) + '</rating>\n')
            #else:
            #    fileh.write('    </rating>\n')

            mpaa = getRatings(id)
            if mpaa != None:
                fileh.write('    <mpaa>US:Rated ' + mpaa + '</mpaa>\n')

            if collection != None:
                fileh.write('    <set>\n        <name>' + collection + '</name>\n')
                fileh.write('    </set>\n')

            if overview != None:
                fileh.write('    <plot>' + overview + '</plot>\n')
                fileh.write('    <outline>' + overview + '</outline>\n')

            if genrelist != None:
                for genre in genrelist:
                    fileh.write('    <genre>' + genre + '</genre>\n')

            if studiolist != None:
                for studio in studiolist:
                    fileh.write('    <studio>' + studio + '</studio>\n')

            if writerlist != None and len(writerlist) > 0:
                for writer in writerlist:
                    fileh.write('    <writer>' + writer + '</writer>\n')

            #if producerlist != None and len(producerlist) > 0:
            #    for producer in producerlist:
            #        fileh.write('    <producer>' + producer + '</producer>\n')

            if directorlist != None and len(directorlist) > 0:
                for director in directorlist:
                    fileh.write('    <director>' + director + '</director>\n')

            #if actorlist != None:
            #    count = 1
            #    for actor in actorlist:
            #        fileh.write('    <actor>\n        <name>' + actor + '</name>\n')
            #        fileh.write('        <type>Actor</type>\n')
            #        fileh.write('        <sortorder>' + str(count) + '</sortorder>\n')
            #        fileh.write('    </actor>\n')
            #        count += 1

            #if trailerlist != None and len(trailerlist) > 0:
            #    for trailer in trailerlist:
            #        fileh.write('    <trailer>' + trailer + '</trailer>\n')    

            fileh.write('</series>\n')
            fileh.close()
   
        mgenlog = ' NFO successful series file creation: \t' + nfofile
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        fileh.close()
        mgenlog = ' There was an error creating the movie NFO file'
        genLog(mgenlog, 'Yes')
        return 0
    

def getArtwork(title, mdata):                # Generate artwork files

    try:
        if 'poster_path' in mdata.keys() and mdata['poster_path'] != None:
            posterurl = poster_base + mdata['poster_path']        
            posterfile = 'nfo\\' + title + '-poster.jpg'
            folderfile =  'nfo\\' + title + '-folder.jpg'           
            resource = urllib.request.urlopen(posterurl)
            output = open(posterfile,"wb")
            output.write(resource.read())
            output.close()
            mgenlog = ' TMDB series poster file created: \t' + posterfile
            genLog(mgenlog, 'Yes')
            resource = urllib.request.urlopen(posterurl)
            output = open(folderfile,"wb")
            output.write(resource.read())
            output.close()
            mgenlog = ' TMDB series folder file created: \t' + folderfile
            genLog(mgenlog, 'Yes')
        else:
            mgenlog = ' No poster file information found on TMDB'
            genLog(mgenlog, 'Yes') 

        if 'backdrop_path' in mdata.keys() and mdata['backdrop_path'] != None:
            backdropurl = backdrop_base + mdata['backdrop_path']        
            backdropfile = 'nfo\\' + title + '-fanart.jpg'        
            resource = urllib.request.urlopen(backdropurl)
            output = open(backdropfile,"wb")
            output.write(resource.read())
            output.close()
            mgenlog = ' TMDB series backdrop file created: \t' + backdropfile
            genLog(mgenlog, 'Yes')
        else:
            mgenlog = ' No backdrop file information found on TMDB'
            genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        mgenlog = ' There was an error creating the movie artwork'
        genLog(mgenlog, 'Yes')
        return 0


def createExtrasFile(title, tmdb_id, vote_average, homepage, producerlist, actorlist, trailerlist):

    try:
        extfile = 'nfo\\' + title + '-extras.txt'
        mgenlog = 'Target Extras file: ' + extfile
        genLog(mgenlog)
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        with io.open(extfile,'w',encoding='utf8') as fileh:
        #fileh = open(extfile, "w")                                       #  Create NFO file
            fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility ' + version + ' -->\n\n')
            fileh.write('These are extras fields which can be cut/pasted into the Mezzmo video properties. \n\n')

            if tmdb_id != None:
                fileh.write('TMDB ID:\t' + str(tmdb_id) + '\n')
            else:
                fileh.write('TMDB ID:\n')

            if vote_average != None:
                fileh.write('Rating:\t\t' + str(round(vote_average / 2)) + '\n')
            else:
                fileh.write('Rating:\t\n')

            if homepage != None:
                fileh.write('Website:\t' + homepage + '\n')
            else:
                fileh.write('Website:\t\n')

            if producerlist != None:
                producerwrite = ''
                for producer in producerlist:
                    producerwrite = producerwrite + producer + ', ' 
                fileh.write('\nProducers:\n' + producerwrite.strip(', ') + '\n')           
            else:
                fileh.write('\nProducers:\n')

            if actorlist != None:
                actorwrite = ''
                for actor in actorlist:
                    actorwrite = actorwrite + actor + ', ' 
                fileh.write('\nActors:\n' + actorwrite.strip(', ') + '\n')           
            else:
                fileh.write('\nActors:\n')

            if trailerlist != None:
                trailerwrite = ''
                for trailer in trailerlist:
                    trailerwrite = trailerwrite + trailer + '\n' 
                fileh.write('\nTrailers:\n' + trailerwrite + '\n')           
            else:
                fileh.write('\nTrailers:\n')
        
            fileh.close()

        mgenlog = ' Extras info file created: \t\t' + extfile
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        mgenlog = ' There was an error creating the movie extras file.'
        genLog(mgenlog, 'Yes')
        return 0


def getRatings(tmdb_id):

        rating_url = ratings_url.format(tmdb_id)

        hencoded = urllib.parse.urlencode(headers)

        parms = {'api_key': tmdb_key,                             #  TMDB URL Parms
                'language': 'en-US',
                'accept': 'application/json',
                'adult': False,                    
                }  

        queryInfo = urllib.parse.urlencode(parms)
        reqnew = urllib.parse.quote(rating_url, safe=':/?')
        request = reqnew + queryInfo

        #print(request)

        jresponse = requests.get(request, headers=headers)
        mdata = jresponse.json()  

        #print(mdata)

        ratings = mdata.get('results')

        for rating in ratings:
            if rating.get('iso_3166_1') == 'US':
                mpaa = rating.get('rating')
                return mpaa

        return None
        

