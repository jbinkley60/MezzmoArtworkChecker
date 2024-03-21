# -*- coding: utf-8 -*-
# #!/usr/bin/python
import urllib.request, urllib.parse, urllib.error
import json, os
from datetime import datetime

base_url = 'https://api.themoviedb.org/3/search/movie?'
movie_url = 'https://api.themoviedb.org/3/movie/{}?'
poster_base = 'https://image.tmdb.org/t/p/w500'
backdrop_base = 'https://image.tmdb.org/t/p/original'
headers = {'User-Agent': 'Mezzmo Artwork Checker 1.0.17'}
tmdb_key = ''

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
            movielist = getMovieList(tmdb_key, movie, rel_year)
            if len(movielist) == 0:
                print('\n No matching movies found')
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
        while counter < len(jdata['results']) and counter < 5:
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
        os.system('cls')
        
        print('\n    Year\t\tTitle\n')
        for x in range(len(movielist)):
            print(' ' + str(movielist[x]['order']) + '.  ' + movielist[x]['year'] + '    '    \
            + movielist[x]['title'])

        choice = -2
        while choice != -1 or choice > len(movielist) - 1:
            choice = int(input('\n Enter number of movie to get details or 0 to exit ?\n')) - 1
            if choice == -1:
                print('User requested to exit.')
                exit()
            elif choice > len(movielist) - 1:
                print(' Invalid entry.  Please select a movie number')
            else:
                break                             

        return movielist[choice]          


    except Exception as e:
        print (e)
        print(' There was an error getting the movie selection')
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
        print('There was an error getting the movie details')
        return 0


def parseMovieDetails(mdata):                                   # Parse JSON movie details data

    try:
        if 'title' in mdata.keys():
            title = mdata['title']
            #print(mdata['title'])
        if 'id' in mdata.keys():
            id = str(mdata['id'])
            #print(mdata['id'])
        if 'imdb_id' in mdata.keys():
            imdb_id = mdata['imdb_id']
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

        nfofile = 'nfo\\' + title + '.nfo'
        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        fileh = open(nfofile, "w")                                       #  Create NFO file
        fileh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility 0.0.17-->\n\n')
        fileh.write('<movie>\n')
        fileh.write('    <title>' + title + '</title>\n')
        fileh.write('    <tmdbid>' + id + '</tmdbid>\n')
        fileh.write('    <imdbid>' + imdb_id + '</imdbid>\n')

        if tagline != None:
            fileh.write('    <tagline>' + tagline + '</tagline>\n')

        if homepage != None:
            fileh.write('    <homepage>' + homepage + '</homepage>\n')

        if release_date != None:
            fileh.write('    <premiered>' + release_date + '</premiered>\n')
            fileh.write('    <year>' + release_year + '</year>\n')

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

        if producerlist != None and len(producerlist) > 0:
            for producer in producerlist:
                fileh.write('    <producer>' + producer + '</producer>\n')

        if directorlist != None and len(directorlist) > 0:
            for director in directorlist:
                fileh.write('    <director>' + director + '</director>\n')

        if actorlist != None:
            count = 1
            for actor in actorlist:
                fileh.write('    <actor>\n        <name>' + actor + '</name>\n')
                fileh.write('        <type>Actor</type>\n')
                fileh.write('        <sortorder>' + str(count) + '</sortorder>\n')
                fileh.write('    </actor>\n')
                count += 1

        if trailerlist != None and len(trailerlist) > 0:
            for trailer in trailerlist:
                fileh.write('    <trailer>' + trailer + '</trailer>\n')    

        fileh.write('</movie>\n')
        fileh.close()
   
        print('NFO successful file creation: \t' + nfofile)


        if 'poster_path' in mdata.keys():
            posterurl = poster_base + mdata['poster_path']        
            posterfile = 'nfo\\' + title + '-poster.jpg'        
            resource = urllib.request.urlopen(posterurl)
            output = open(posterfile,"wb")
            output.write(resource.read())
            output.close()
            print(' TMDB poster file created: \t' + posterfile)
        else:
            print(' No poster file information found on TMDB') 

        if 'backdrop_path' in mdata.keys():
            backdropurl = backdrop_base + mdata['backdrop_path']        
            backdropfile = 'nfo\\' + title + '-fanart.jpg'        
            resource = urllib.request.urlopen(backdropurl)
            output = open(backdropfile,"wb")
            output.write(resource.read())
            output.close()
            print(' TMDB backdrop file created: \t' + backdropfile)
        else:
            print(' No backdrop file information found on TMDB') 

    except Exception as e:
        print (e)
        print(' There was an error parsing the movie details')
        return 0    