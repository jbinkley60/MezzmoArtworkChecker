# -*- coding: utf-8 -*-
# #!/usr/bin/python
import urllib.request, urllib.parse, urllib.error
import json, os, io
from datetime import datetime
from common import genLog, openActorDB
from actor_tmdb import getImage, actorFile

base_url = 'https://api.themoviedb.org/3/search/movie?'
movie_url = 'https://api.themoviedb.org/3/movie/{}?'
poster_base = 'https://image.tmdb.org/t/p/w500'
backdrop_base = 'https://image.tmdb.org/t/p/original'
headers = {'User-Agent': 'Mezzmo Artwork Checker 1.0.17'}
tmdb_key = ''
file = ''

def nfoMenu(key):                                         # NFO Main Menu

    try:
        global tmdb_key
        tmdb_key = key

        movie = rel_year = ''

        os.system('cls')
        print('\t\tMezzmo NFO Utility\n')

        print(' 1.  Creates NFO file based upon title')
        print(' 2.  Scrapes movies in NFO folder.  Future\n\n')

        choice = input(' Enter NFO command  ?\n')
        if choice == '1':                              
            movie = input(' Enter movie title  (i.e. Star Wars) ?\n')
            rel_year = input(' Enter movie year or hit enter to leave blank (i.e. 1977) ?\n')
            print('\n')
            mgenlog = 'NFO movie search on: ' + movie + ' ' + rel_year
            genLog(mgenlog)
            movielist = getMovieList(tmdb_key, movie, rel_year)
            if len(movielist) == 0:
                mgenlog = 'No matching movies found'
                print('\n No matching movies found')
                #genLog(mgenlog, 'Yes')
                exit()
            else:
                movieselection = getMovieSelection(movielist)
            if movieselection == 0:
                print('\n No movie selected')

            else:
                moviedetails = getMovieDetails(tmdb_key, movieselection)
            if moviedetails == 0:
                print(' No movie details received.')
            else:
                parseMovieDetails(moviedetails)    
        elif choice == '2':
            print('\n Scraping feature not implemented yet.')
        else:
            print(' No valid entry found.')

    except Exception as e:
        print (e)
        print(' There was an error getting the NFO menu')     
           

def getMovieList(tmdb_key, movie, rel_year):

    try:
        movielist = []
        hencoded = urllib.parse.urlencode(headers)

        parms = {'api_key': tmdb_key,                      #  TMDB URL Parms
                'language': 'en-US',
                'accept': 'application/json',
                'adult': False,
                'primary_release_year': rel_year,                      
                'query': movie,
                }  

        queryInfo = urllib.parse.urlencode(parms)
        reqnew = urllib.parse.quote(base_url, safe=':/?')
        request = reqnew + queryInfo

        #print(request)

        req = urllib.request.Request(request, headers=headers)
        jresponse = urllib.request.urlopen(req)

        jdata = json.load(jresponse)

        #print(str(jdata))

        counter = 0
        while counter < len(jdata['results']) and counter < 10:
            currmovie = {} 
            currmovie['order'] = counter + 1    
            currmovie['title'] = (jdata['results'][counter]['title'])
            currmovie['year'] = (jdata['results'][counter]['release_date'][:4])
            currmovie['tmdb_id'] = (jdata['results'][counter]['id'])
            currmovie['overview'] = (jdata['results'][counter]['overview'])
            counter += 1
            #print(year[:4] + '\t' + title)
            movielist.append(currmovie)
            #print(str(counter))
            #print(str(currmovie))
            del currmovie
        #print(str(movielist))
        return movielist

    except Exception as e:
        print (e)
        print(' There was an error getting the movie ID')
        return movielist 


def getMovieSelection(movielist):                    # Get Movie selection   

    try:
        global file
        os.system('cls')
        
        print('\n    Year\t\tTitle\t\t\t\t\t\tOverview\n')
        for x in range(len(movielist)):
            if len(movielist[x]['year']) < 4:
                year = '    '
            else:
                year = movielist[x]['year']
            if x < 9:
                #print(' ' + str(movielist[x]['order']) + '.  ' + year + '    '    \
                #+ movielist[x]['title'])
                print(' ' + str(movielist[x]['order']) + '.  ' + year + '    '    \
                + "{:<48}".format(movielist[x]['title'][:44]) + movielist[x]['overview'][:70])

            else:
                print(' ' + str(movielist[x]['order']) + '. ' + year + '    '    \
                + movielist[x]['title']) 

        choice = -2
        while choice != -1 or choice > len(movielist) - 1:
            choice = input('\n Enter number of movie to get details or 0 to exit ?\n')
            if len(choice) > 0 and str(choice).isdigit() and int(choice) != 0:     # Vaild entry
                choice = int(choice) - 1
            elif len(choice) == 0 or str(choice).isdigit() and int(choice) == 0:   # User exit
                mgenlog = 'User requested to exit.'
                genLog(mgenlog, 'Yes')
                exit()
            if not str(choice).isdigit() or choice > len(movielist) - 1:           # Invalid entry
                print(' Invalid entry.  Please select a movie number')
                choice = -2
            elif choice > -1 and choice < len(movielist):                          # Valid entry
                mgenlog = 'User selected ' + str(choice + 1) + ' - ' + movielist[choice]['title']
                genLog(mgenlog)
                break

        print ('\n Hit enter to use movie title as the NFO name or enter a new file ')
        choice2 = input(' name to use.  (i.e. Road House 2024)  ?\n')
        if len(choice2) > 0:
            file = choice2
            mgenlog = 'User entered custom NFO file name: ' + choice2
            genLog(mgenlog)
        return movielist[choice]          


    except Exception as e:
        print (e)
        mgenlog = ' There was an error getting the movie selection'
        genLog(mgenlog, 'Yes')
        return 0 


def getMovieDetails(tmdb_key, movieselection):                    # Get Movie details   

    try:
        os.system('cls')
        #print(str(movieselection))

        tmdb_id = movieselection['tmdb_id']
        details_url = movie_url.format(tmdb_id)

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

        req = urllib.request.Request(request, headers=headers)
        jresponse = urllib.request.urlopen(req)

        mdata = json.load(jresponse)

        #print(str(mdata))
        return(mdata)


    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting the movie details'
        genLog(mgenlog, 'Yes')
        return 0


def parseMovieDetails(mdata):                                   # Parse JSON movie details data

    try:
        global file
        if 'title' in mdata.keys():
            if len(file) > 0:                                   # Use file name from user
                title = file
            else:
                title = mdata['title']
            print(title)
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
        if 'release_date' in mdata.keys():
            release_date = mdata['release_date']
            release_year = mdata['release_date'][:4]
            #print(mdata['release_date'])
            #print(mdata['release_date'][:4])
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

        createNfoFile(title, id, imdb_id, tagline, homepage, release_date, mpaa, collection, overview, \
        genrelist, studiolist, writerlist, producerlist, directorlist, actorlist, trailerlist)
        getArtwork(title, mdata)
        createExtrasFile(title, id, vote_average, homepage, producerlist, actorlist, trailerlist)
        choice3 = input('\n Would you like to check for new actor / actress artwork (Y/N) ?\n')
        if choice3.lower() =='y':
            print('\n')
            mgenlog = 'User chose to check for new actor artwork'
            genLog(mgenlog)
            checkActorImages(actorlist)
        mgenlog = ' Mezzmo Artwork Checker NFO creation process completed.'
        genLog(mgenlog, 'Yes')       

    except Exception as e:
        print (e)
        print(' There was an error parsing the movie details')
        return 0


def createNfoFile(title, id, imdb_id, tagline, homepage, release_date, mpaa, collection, overview, \
    genrelist, studiolist, writerlist, producerlist, directorlist, actorlist, trailerlist): 

    try:
        nfofile = 'nfo\\' + title + '.nfo'
        mgenlog = 'Target NFO file: ' + nfofile
        genLog(mgenlog)
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        #fileh = open(nfofile, "w")                                       #  Create NFO file
        with io.open(nfofile,'w',encoding='utf8') as fileh:
            fileh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility 1.0.17-->\n\n')
            fileh.write('<movie>\n')
            fileh.write('    <title>' + title + '</title>\n')
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

            fileh.write('</movie>\n')
            fileh.close()
   
        mgenlog = ' NFO successful file creation: \t' + nfofile
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        fileh.close()
        mgenlog = ' There was an error creating the movie NFO file'
        genLog(mgenlog, 'Yes')
        return 0
    

def getArtwork(title, mdata):                # Generate artwork files

    try:
        if 'poster_path' in mdata.keys():
            posterurl = poster_base + mdata['poster_path']        
            posterfile = 'nfo\\' + title + '-poster.jpg'        
            resource = urllib.request.urlopen(posterurl)
            output = open(posterfile,"wb")
            output.write(resource.read())
            output.close()
            mgenlog = ' TMDB poster file created: \t' + posterfile
            genLog(mgenlog, 'Yes')
        else:
            mgenlog = ' No poster file information found on TMDB'
            genLog(mgenlog, 'Yes') 

        if 'backdrop_path' in mdata.keys():
            backdropurl = backdrop_base + mdata['backdrop_path']        
            backdropfile = 'nfo\\' + title + '-fanart.jpg'        
            resource = urllib.request.urlopen(backdropurl)
            output = open(backdropfile,"wb")
            output.write(resource.read())
            output.close()
            mgenlog = ' TMDB backdrop file created: \t' + backdropfile
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
            fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility 1.0.17-->\n\n')
            fileh.write('These are extras fields which can be cut/pasted into the Mezzmo video properites. \n\n')

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

        mgenlog = ' Extras info file created: \t' + extfile
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        mgenlog = ' There was an error creating the movie extras file.'
        genLog(mgenlog, 'Yes')
        return 0


def checkActorImages(actorlist):                    # Search for actor images

    try:

        mgenlog = 'Beginning NFO actor image search.'
        genLog(mgenlog, 'Yes')

        actdb = openActorDB()

        if len(actorlist) == 0:
            mgenlog('No actors found in movie to generate NFO images.')
            actdb.close()
            return

        fetchlist = []
        imgfound = 0

        for actor in actorlist:

            srchactor = actor + "%"
            cura = actdb.execute('SELECT actor from actorArtwork WHERE actor like ?',     \
            (srchactor,))
            actortuple = cura.fetchone()
            if not actortuple:
                #print('Actor not found in database: ' + actor)
                result = getImage(tmdb_key, actor, 'search') 
                if result == 'tmdb_found':
                    imgfound += 1
            cura = actdb.execute('SELECT actor from actorArtwork WHERE actor like ? AND   \
            (posterFile IS NULL or posterFile = "") AND (userPosterFile IS NULL OR        \
            userPosterFile =="")',(srchactor,))  #  Check actorArtwork
            actortuple = cura.fetchone()

            if actortuple:          
                #print('Actor image not found: ' + actor)
                result = getImage(tmdb_key, actor, 'search')
                if result == 'tmdb_found':
                    imgfound += 1
        actdb.close()

        mgenlog = 'NFO actor image search completed.'
        genLog(mgenlog, 'Yes')
        print('\n')
        mgenlog = 'Actors checked for images:\t' + str(len(actorlist))
        genLog(mgenlog, 'Yes')
        mgenlog = 'Actor images downloaded:\t' + str(imgfound)
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        mgenlog = ' There was an error creating the movie NFO actor images.'
        genLog(mgenlog, 'Yes')
        return 0
    