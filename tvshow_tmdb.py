# -*- coding: utf-8 -*-
# #!/usr/bin/python
import urllib.request, urllib.parse, urllib.error
import json, os, io, sys, time
import requests
from datetime import datetime
from common import genLog, openActorDB, openMezzmoDB, makeMezzmoBackups
from actor_tmdb import actorFile
from unidecode import unidecode

base_url = 'https://api.themoviedb.org/3/search/tv?'
tvshow_url = 'https://api.themoviedb.org/3/tv/{}?'
episode_url = 'https://api.themoviedb.org/3/tv/{}/season/{}/episode/{}?'
episode_credits_url = 'https://api.themoviedb.org/3/tv/{}/season/{}/episode/{}/credits?'
ratings_url = 'https://api.themoviedb.org/3/tv/{}/content_ratings?'
poster_base = 'https://image.tmdb.org/t/p/w500'
backdrop_base = 'https://image.tmdb.org/t/p/original'
version_name = 'version v1.0.24'
version  = "1.0.24"
headers = {'User-Agent': 'Mezzmo Artwork Checker ' + version}
tmdb_key = ''
imgsize = "w300"
file = ''

def selectTVshow(key, imagesize):                       # Select TV Show from TMDB

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


def selectMezzmoTVShow(key, option, nfochoice, mezzmoposterpath, imagesize, mezzmopath, mezzconn, mezzfull = 'yes', direct = 0):  # Searches Mezzmo database for a list of matching TV shows

        tvshow =  ''
        tvshow = input('\n Enter TV Show series title  (i.e. Happy Days) ?\n')
        if len(tvshow) < 2:
            return
        if option == 'nfo':  
            mgenlog = 'User selected to create episode NFO file(s) for series: ' + tvshow
            genLog(mgenlog)
        else:
            mgenlog = 'User selected to update Mezzmo episode metadata for series: ' + tvshow
            genLog(mgenlog)

        db = openMezzmoDB(mezzconn)
        #genLog('Mezzfull: ' + mezzfull + ' ' + str(len(mezzfull)))
        target = "%" + tvshow + "%"
        if mezzfull == 'no':
            dbcurr = db.execute('SELECT ID, Data from MGOFileAlbum where Data like ?', (target,))
        else:
            dbcurr = db.execute('SELECT DISTINCT MGOfileAlbum.ID, Data from MGOFileAlbum inner join \
            MGOFileAlbumRelationship on MGOfileAlbum.ID = MGOFileAlbumRelationship.ID inner join    \
            MGOFile on MGOFileAlbumRelationship.FileID = MGOFile.ID where TypeUID = 4 and Data      \
            like ? and track > 0 ORDER BY YEAR', (target,))
        dbtuples = dbcurr.fetchall()
        del dbcurr
        
        mgenlog = 'The number of TV Show matches: ' + str(len(dbtuples))
        genLog(mgenlog)

        if len(dbtuples) > 1:
            # print(str(dbtuples))
            os.system('cls')
            if option == 'nfo':             
                print("\t\tSelect TV Show Series to Create Episode NFO files\n\n")
            else:
                print("\t\tSelect TV Show Series to Update Mezzmo Episode metadata\n\n")
            for x in range(len(dbtuples)):
                print(str(x+1) + "\t" + dbtuples[x][1])
            choice = input('\n Enter number of TV Show to get episodes or 0 to exit ?\n')          
            if choice == "0":
                db.close()
                return
            else:
                tvshow = dbtuples[int(choice) - 1][1]
                seriesID = str(dbtuples[int(choice) - 1][0])
        elif len(dbtuples) == 1:
            tvshow = dbtuples[0][1]
            seriesID =  str(dbtuples[0][0])
            print('\n')
            mgenlog = 'Exact series match found in Mezzmo: ' + dbtuples[0][1]
            genLog(mgenlog, 'Yes')
        else:
            mgenlog = 'There were no matching TV Show Series found in the Mezzmo database.'
            genLog(mgenlog, 'Yes')
            print('Please ensure that Mezzmo has discovered the associated media files and confirm the series name.')
            db.close()
            return
        mgenlog = 'Mezzmo TV Show selected: ' + seriesID
        genLog(mgenlog)
        #print(tvshow + "  " + seriesID)

        season =  input('\n Enter season number to get episodes or 0 for all seasons ?\n')
        if season != '0' and len(season) != 0:
            episode =  input('\n Enter episode number to get episode or 0 for all episodes ?\n')
            season_print = season
            if episode == '0' or len(episode) == 0:
                episode = '%'
                episode_print = "All"
            else:
                episode_print = episode
        elif season == '0' or len(season) == 0:
            season = '%'
            episode = '%'
            season_print = "All" 
            episode_print = "All"

        mgenlog = 'User entered season: ' + season_print + '  episode: ' + episode_print
        genLog(mgenlog)
        #print("Disc and track: " + season + ' ' + episode)

        decurr = db.execute('select MGOFile.File, MGOFile.Disc, MGOFile.Track, MGOFile.ID from MGOFile  \
        inner join MGOFileAlbumRelationship on MGOfile.ID = MGOFileAlbumRelationship.FileID             \
        where MGOFileAlbumRelationship.ID = ? and disc like ? and track like ? ORDER BY disc,           \
        track', (seriesID, season , episode,))

        detuples = decurr.fetchall()
        del decurr
        db.close()

        if len(detuples) == 0:
            mgenlog = 'There were no matching TV Show Episodes found in the Mezzmo database.'
            genLog(mgenlog, 'Yes')
            print('Please ensure that Mezzmo has discovered the assocaited media files and confirm the series name.')
            return
        else:
            mgenlog = 'Matching TV Show Episodes found in Mezzmo: ' + str(len(detuples))
            genLog(mgenlog, 'Yes')
            time.sleep(2)

        tvshowlist = getTVShowList(key, tvshow, '')
        if len(tvshowlist) == 0:
            mgenlog = 'No matching TV Shows found on TMDB'
            genLog(mgenlog, 'Yes')
            sys.exit()
        else:
            tvselection = getTvShowSelection(tvshowlist, 'yes')

        #print(tvselection)
        #print(detuples)
        print('Direct: ' + str(direct))

        sdata = getTVShowDetails(key, tvselection)
        #print(sdata)
        #paused = input('Hit Enter to continue')

        if direct == 1:
            mezzmo_on = input('Have you checked to ensure the Mezzmo service and GUI are not running (Y/N) ?  ')
            if mezzmo_on.lower() != 'y':
                mgenlog = 'User did not confirm Mezzmo shutdown.  Aborting direct Mezzmo DB updates.'
                genLog(mgenlog)
                return

            bkup = input('Would you like to backup your Mezzmo database before making updates (Y/N) ? ' )
            if 'y' in bkup:
                makeMezzmoBackups(mezzmopath)

            print("\n")
            mgenlog = 'Beginning Mezzmo metadata direct database updates.'
            genLog(mgenlog, 'yes')
            time.sleep(1.5)            
               
        artworklists = []
        for x in range(len(detuples)):
            season = detuples[x][1]
            episode = detuples[x][2]
            epdata = getTVEpisodeDetails(key, tvselection, season, episode)
            rfpos = detuples[x][0].rfind('\\')
            rfpos1 = detuples[x][0].rfind('.')
            fname = "nfo\\" + detuples[x][0][rfpos+1:rfpos1] + ".nfo"

            #print(fname)
            #print(str(epdata))
            #paused = input('Hit Enter to continue')

            #return
            if epdata != 0:                                                        # Episode found on TMDB
                episode_dict = parseEpisodedata(tvshow, season, episode, epdata, sdata)
                #print(episode_dict)

                actorlist = episode_dict.get('actorlist', None)                        # Build actor list for artwork fetching
                if actorlist != None:
                    for actor in actorlist:
                        if actor[0] not in str(artworklists):
                            #print(actor[0])
                            artworklists.append(actor)

                if episode_dict != 0  and direct == 0:
                    nfofile = createEpisodeNfoFile(fname, tvshow, episode_dict)        # Create episode NFO file
                elif episode_dict != 0  and direct == 1:
                    #print('MGOfile ID: ' + str(detuples[x][3]) + '\n')
                    #print(episode_dict)
                    file_id = detuples[x][3]
                    updateMezzmoEpisode(file_id, episode_dict, mezzconn)
                    #print('\n' + episode_dict.get('actorlist')[0][0])
                    nfofile = 0
                
                if nfofile != 0:
                    mgenlog = ' NFO successful series file creation: \t' + nfofile
                    genLog(mgenlog, 'Yes')
            #print(artworklists)
            #print('Number of actors found: ' + str(len(artworklists)))

        choice3 = input('\n Would you like to check for new actor / actress artwork (Y/N) ?  ')
        if choice3.lower() =='y':
            print('\n')
            mgenlog = 'User chose to check for new actor artwork'
            genLog(mgenlog)
        else:
            return

        userposters = getTvUserPosterFiles(mezzmoposterpath)                         # Get current list of local and remote userposter folder
        for actor in artworklists:
            actor_name = actorFile(actor[0])                                         # Convert to userposter format
            #print(actor_name)
            useractor = nameConvert(actor_name )                                     # Remove unicode characters
            #print(useractor)
            if useractor.lower() in userposters:
                mgenlog = actor[0] + ' poster file found in userposter folder.'
                genLog(mgenlog, 'yes')
            elif actor[2] != None:
                #print('notfound')
                getActorImage(actor[2], useractor.lower(), imagesize)                # Fetch missing actor poster image

        mgenlog = 'Actor artwork fetching completed.'
        genLog(mgenlog, 'yes')


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

        #print(str(jdata))
        #print('The number of TV Show matches is: ' + str(len(jdata))) 
        #input('Press enter to continue')     
 
        counter = 0
        while counter < len(jdata['results']) and counter < 10:
            currshow = {} 
            currshow['order'] = counter + 1    
            currshow['title'] = (jdata['results'][counter]['name'])
            currshow['year'] = (jdata['results'][counter]['first_air_date'][:4])
            currshow['tmdb_id'] = (jdata['results'][counter]['id'])
            currshow['overview'] = (jdata['results'][counter]['overview'])
            currshow['original_language'] = (jdata['results'][counter]['original_language'])
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


def getTvShowSelection(tvshowlist, episodes = ''):                    # Get TV Show selection   

    try:
        global file
        os.system('cls')
        
        print('\n    Year\t\tTitle\t\t\t\t\t\tOverview\n')
        for x in range(len(tvshowlist)):
            if tvshowlist[x]['original_language'] == 'en':            # Only display Enlglish shows
                #genLog(tvshowlist[x]['original_language'])
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
        tmdb_id = 0
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
                tmdb_id = tvshowlist[choice]['tmdb_id']
                mgenlog = 'User selected ' + str(choice + 1) + ' - ' + str(tmdb_id) + ' - ' + tvshowlist[choice]['title']
                genLog(mgenlog)
                break

        if episodes == 'yes':                                      # If episodes NFO return selection
            return tvshowlist[choice]    
             
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
                'append_to_response': 'casts,trailers,releases,content_ratings',
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
        id = mdata.get('id', None)
        imdb_id = mdata.get('imdb_id', None)
        tagline = mdata.get('tagline', None)
        homepage = mdata.get('homepage', None)

        #if 'id' in mdata.keys():
        #    id = str(mdata['id'])
        #else:
        #    id = None
        #print(mdata['id'])
        #if 'imdb_id' in mdata.keys():
        #    imdb_id = mdata['imdb_id']
        #else:
        #    imdb_id = None
        #    #print(mdata['imdb_id'])
        #if 'tagline' in mdata.keys() and len(mdata['tagline']) > 0:
        #    tagline = mdata['tagline']
        #    #print(mdata['tagline'])
        #else:
        #    tagline = None   
        #if 'homepage' in mdata.keys() and len(mdata['homepage']) > 0:
        #    homepage = mdata['homepage']
        #    #print(mdata['homepage'])
        #else:
        #    homepage = None
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
            #for genre in range(len(genres)):
            #    genrelist.append(genres[genre]['name'])
            for genre_item in range(len(genres)):
                genre_items = genres[genre_item]['name']
                genre_items = genre_items.replace(' & ', ',').replace('Sci-Fi', 'Science Fiction').split(',')
                for genre in range(len(genre_items)):
                    genrelist.append(genre_items[genre]) 
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
        miniseries = input('Generate Full or Minimum series.xml file (M/F) ?  Full is Default.  ')
        with io.open(nfofile,'w',encoding='utf8') as fileh:
            fileh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility ' + version + ' -->\n\n')
            fileh.write('<series>\n')
            fileh.write('    <seriesname>' + title + '</seriesname>\n')
            if miniseries.lower() == 'm':
                fileh.write('</series>\n')
                fileh.close()
                mgenlog = ' Minimal successful series.xml file creation: \t' + nfofile
                genLog(mgenlog, 'Yes')
                return                         
            if id != None:
                fileh.write('    <tmdbid>' + str(id) + '</tmdbid>\n')

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
   
        mgenlog = ' Full successful series.xml file creation: \t' + nfofile
        genLog(mgenlog, 'Yes')

    except Exception as e:
        print (e)
        fileh.close()
        mgenlog = ' There was an error creating the TV Show series.xml file'
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


def getTVEpisodeDetails(tmdb_key, tvselection, season, episode):    # Get TV  details  

    try:
        #os.system('cls')
        #print(str(tvselection))

        tmdb_id = tvselection['tmdb_id']
        details_url = episode_url.format(tmdb_id, season, episode)

        hencoded = urllib.parse.urlencode(headers)

        #print(details_url)

        parms = {'api_key': tmdb_key,                             #  TMDB URL Parms
                'language': 'en-US',
                'accept': 'application/json',
                'adult': False,
                'append_to_response': 'credits, releases',                    
                }  

        queryInfo = urllib.parse.urlencode(parms)
        reqnew = urllib.parse.quote(details_url, safe=':/?')
        request = reqnew + queryInfo

        #print(request)

        jresponse = requests.get(request, headers=headers)
        mdata = jresponse.json()
        #print(str(mdata))

        if jresponse.status_code != 200:                            # Check for TMDB 200 response
            mgenlog = 'Episode not found on TMDB skipping: ' + str(jresponse.status_code) + ' ' + tvselection['title'] \
            + '  Season: ' + str(season) + '  Episode: ' + str(episode) 
            genLog(mgenlog, 'yes')
            return 0
        else:
            return(mdata)

    except Exception as e:
        print (e)
        mgenlog = 'There was an error getting the TV Show Episode details'
        genLog(mgenlog, 'Yes')
        return 0


def createEpisodeNfoFile(nfofile, tvshow, episode_dict):  # Create episode NFO file

    try:
        indent = "    "
        title = episode_dict.get('title', None)
        sorttitle = episode_dict.get('sorttitle', None)
        plot = episode_dict.get('overview', None)
        premiered = episode_dict.get('premiered', None)
        release_year = episode_dict.get('release_year', None)
        tmdb_id = episode_dict.get('tmdb_id', None)
        website = episode_dict.get('website', None)
        rating = episode_dict.get('eprating', None)
        mpaa = episode_dict.get('mpaa', None)
        season = episode_dict.get('season', None)
        episode = episode_dict.get('episode', None)
        studiolist = episode_dict.get('studiolist', None)
        genrelist = episode_dict.get('genrelist', None)
        rating_data = episode_dict.get('mpaa', None)
        writerlist = episode_dict.get('writerlist', None)
        producerlist = episode_dict.get('producerlist', None)
        directorlist = episode_dict.get('directorlist', None)
        actorlist = episode_dict.get('actorlist', None)

        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        #fileh = open(nfofile, "w")                                       #  Create NFO file
        with io.open(nfofile,'w',encoding='utf8') as fileh:
            fileh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            fileh.write('<!--created on ' + currTime + ' - Mezzmo Artwork Checker NFO utility ' + version + ' -->\n\n')
            fileh.write('<movie>\n')
            if title != None:
                fileh.write(indent + '<title>' + title + '</title>\n')
                fileh.write(indent + '<SortTitle>' + sorttitle + '</SortTitle>\n')
            if plot != None:
                fileh.write(indent + '<plot>' + plot + '</plot>\n')
                fileh.write(indent + '<outline>' + plot + '</outline>\n')
            if premiered != None:
                fileh.write(indent + '<year>' + release_year + '</year>\n')
                fileh.write(indent + '<premiered>' + premiered + '</premiered>\n')
            fileh.write(indent + '<SeriesName>' + tvshow + '</SeriesName>\n')
            if season != None:
                fileh.write(indent + '<season>' + str(season) + '</season>\n')
            if episode != None:
                fileh.write(indent + '<episode>' + str(episode) + '</episode>\n')
            if rating_data != None:
                fileh.write(indent + '<mpaa>' + mpaa + '</mpaa>\n')
            if website != None: 
                fileh.write(indent + '<website>' + website + '</website>\n')

            if studiolist != None and len(studiolist) > 0:
                for studio in studiolist:
                    fileh.write(indent + '<studio>' + studio + '</studio>\n')

            if genrelist != None and len(genrelist) > 0:
                for genre_item in genrelist:
                    #print('Genre item: ' + genre_item)
                    genre_items = genre_item.replace(' & ', ',').replace('Sci-Fi', 'Science Fiction').split(',')
                    #print('Genre item after: ' + str(genre_items))
                    for genre in genre_items:
                        fileh.write(indent + '<genre>' + genre + '</genre>\n')

            if writerlist != None and len(writerlist) > 0:
                for writer in writerlist:
                    fileh.write(indent + '<writer>' + writer + '</writer>\n')

            if directorlist != None and len(directorlist) > 0:
                for director in directorlist:
                    fileh.write(indent + '<director>' + director + '</director>\n')

            if actorlist != None and len(actorlist) > 0:
                for actor in actorlist:
                    fileh.write(indent + '<actor>\n')
                    fileh.write(indent + indent + '<name>' + actor[0] + '</name>\n')                    
                    fileh.write(indent + indent + '<type>Actor</type>\n')                    
                    fileh.write(indent + indent + '<sortorder>' + actor[1] + '</sortorder>\n')                    
                    fileh.write(indent + '</actor>\n')
            fileh.write('</movie>\n')
            fileh.close()
        return nfofile

    except Exception as e:
        print (e)
        fileh.close()
        mgenlog = ' There was an error creating the episode NFO file'
        genLog(mgenlog, 'Yes')
        return 0


def parseEpisodedata(tvshow, season, episode, epdata, sdata):       # Parse Episode data and create episode dictionary

    try:
        #json_print(sdata)

        episode_dict = {}
        title = epdata.get('name', None)
        if title != None:
            title_split = title.split(' ' , 1)
            #print(title_split)
            if title_split[0].lower() in ['a', 'an', 'the']: 
               sort_title = title_split[1] + ', ' + title_split[0]
            else:
                sort_title = title
            #print(sort_title)

        plot = epdata.get('overview', None)
        tmdb_id = epdata.get('id', None)
        vote_average = epdata.get('vote_average', 0)
        if vote_average != 0:
            eprating = str(round(vote_average / 2))
        else:
            eprating = '0'
        website = sdata.get('homepage', None)

        premiered = epdata.get('air_date', None)
        if premiered != None:
            release_year = premiered[:4]
        else:
            release_year = None

        production_companies = sdata.get('production_companies', None)
        if production_companies != None:
            studiolist = []
            for company in range(len(production_companies)):
                name = production_companies[company]['name']
                if name not in str(studiolist):
                    studiolist.append(production_companies[company]['name'])
        else:
            studiolist = None

        genres = sdata.get('genres', None)
        if genres != None:
            genrelist = []
            for genre_item in range(len(genres)):
                genre_items = genres[genre_item]['name']
                genre_items = genre_items.replace(' & ', ',').replace('Sci-Fi', 'Science Fiction').split(',')
                for genre in range(len(genre_items)):
                    genrelist.append(genre_items[genre])
        else:
            genrelist = None

        rating_data = sdata.get('content_ratings', None)
        if rating_data != None:
            ratings = rating_data.get('results')
            mpaa = 'NR'
            for rating in range(len(ratings)):
                country = ratings[rating]['iso_3166_1']
                mpaa = ratings[rating]['rating'] 
                if country == 'US':
                    break
        else:
            mpaa = 'Not Rated'
       
        credits = epdata.get('credits', None)
        #print(epdata) 
        if 'casts' != None:
            crews = credits.get('crew')
            guests = epdata.get('guest_stars', None)
            producerlist = []
            directorlist = []
            writerlist = []
            for crew in range(len(crews)):
                name = None
                name = crews[crew]['name']
                department = crews[crew]['department']
                job = crews[crew]['job']
                if department.lower() in ['writing'] and job.lower() in       \
                ['writer', 'screenplay', 'short story']:
                    if name not in str(writerlist):
                        writerlist.append(name)
                elif department.lower() in ['production'] and 'producer' in   \
                job.lower():
                    if name not in str(producerlist):
                        producerlist.append(name)
                elif department.lower() in ['directing'] and 'director' in    \
                job.lower():
                    if name not in str(directorlist):
                        directorlist.append(name)

            cast = credits.get('cast', None)
            #print(cast)
            actorlist = []
            actcount = 0
            if cast != None:
                for actor in range(len(cast)):
                    role = cast[actor]['known_for_department']
                    name = cast[actor]['name']
                    userposter = cast[actor]['profile_path']
                    if role == 'Acting':
                        if name not in str(actorlist):
                            order = str(actcount)
                            actorlist.append([name, order, userposter])
                            actcount += 1
            #print(guests)
            if guests != None:
                for actor in range(len(guests)):
                    role = guests[actor]['known_for_department']
                    name = guests[actor]['name']
                    userposter = guests[actor]['profile_path']
                    if role == 'Acting':
                        if name not in str(actorlist):
                            order = str(actcount)
                            actorlist.append([name, order, userposter])
                            actcount += 1

            #print(str(actorlist))
        else:
            writerlist = None
            producerlist = None
            directorlist = None
            actorlist = None

        episode_dict['title'] = title
        episode_dict['sorttitle'] = sort_title
        episode_dict['plot'] = plot
        episode_dict['overview'] = plot
        episode_dict['tvshow'] = tvshow      
        episode_dict['season'] = season
        episode_dict['episode'] = episode
        episode_dict['tmdb_id'] = tmdb_id
        episode_dict['rating'] = eprating   
        episode_dict['premiered'] = premiered
        episode_dict['release_year'] = release_year
        episode_dict['mpaa'] = mpaa
        episode_dict['website'] = website   
        episode_dict['genrelist'] = genrelist
        episode_dict['studiolist'] = studiolist
        episode_dict['writerlist'] = writerlist
        episode_dict['producerlist'] = producerlist
        episode_dict['directorlist'] = directorlist
        episode_dict['actorlist'] = actorlist
  
        #print(sdata)

        return episode_dict

    except Exception as e:
        print (e)
        fileh.close()
        mgenlog = ' There was an error parsing the episode JSON data from TMDB'
        genLog(mgenlog, 'Yes')
        return 0


def updateMezzmoEpisode(file_id, episode_dict, mezzconn):              # Update Mezzmo Episode data

    try:
        db = openMezzmoDB(mezzconn)
        title = episode_dict.get('title', '')
        sorttitle = episode_dict.get('sorttitle', '')
        plot = episode_dict.get('overview', '')
        premiered = episode_dict.get('premiered', '')
        tvshow = episode_dict.get('tvshow', 'Not found')
        season = episode_dict.get('season', 0)
        episode = episode_dict.get('episode', 0)
        tmdb_id = str(episode_dict.get('tmdb_id', ''))
        website = episode_dict.get('website', '')
        rating = int(episode_dict.get('rating', '0'))
        mpaa = episode_dict.get('mpaa', '')
        genrelist = episode_dict.get('genrelist', None)
        actorlist = episode_dict.get('actorlist', None)
        studiolist = episode_dict.get('studiolist', None)
        writerlist = episode_dict.get('writerlist', None)
        producerlist = episode_dict.get('producerlist', None)
        directorlist = episode_dict.get('directorlist', None)

        lkcurr = db.execute('SELECT Lock from MGOFile WHERE ID = ?', (file_id,))      # Check for media file lock
        lktuple = lkcurr.fetchone()
        if not lktuple or lktuple[0] == 1:
            mgenlog = 'Unable to update Mezzmo MGOFile table due to lock on media file'
            genLog(mgenlog, 'yes')
            mgenlog = tvshow + '  Season: ' + str(season) + '  Episode: ' + str(episode)
            genLog(mgenlog, 'yes')
            lockinput = input('Do you want to contineu with the Mezzmo metadata updates (Y/N) ? ')
            if 'y' in lockinput.lower():
                mgenlog = 'Continuing Mezzmo metadata updates'
                genLog(mgenlog)
            else:
                mgenlog = 'User chose to not override the Mezzmo media lock.'
                genLog(mgenlog)
                db.close()
                return
        else:
            mgenlog = 'Mezzmo update beginning: ' + tvshow + '  Season: ' + str(season) + '  Episode: ' + str(episode)
            genLog(mgenlog, 'yes')

        try:                                               # Convert date time values for Mezzmo DB format
            past_datetime = datetime.strptime("1899-12-30", "%Y-%m-%d")
            new_datetime = datetime.strptime(premiered, "%Y-%m-%d")
            days_since = float((new_datetime - past_datetime).days)
            month = new_datetime.month
            year = new_datetime.year
        except:
            days_since = 0.0
            month = 0
            year = 0
            mgenlog = 'An error occurred converting the premiered date'
            genLog(mgenlog) 

        #print(title + '  ' + plot + '  ' + mpaa + '  ' + premiered + '  ' + tmdb_id + '  ' + website +  sorttitle)
        #print('Release date and month: ' + str(days_since) + ' ' + str(month))

        dccurr = db.execute('SELECT ID FROM MGOFileContentRating WHERE           \
        ContentRating=?', (mpaa,))
        dctuple = dccurr.fetchone()
        del dccurr

        if dctuple:                                        # Lookup Content Rating / Index in Mezzmo
            crating = dctuple[0]
        else:
            crating = 0         
         

        #  Need to directors and producers

        db.execute('UPDATE MGOfile set Title=?, Description=?, Ranking=?, Month=?,     \
        ReleaseDate=?, Year=?, TheMovieDb_ID=?, URL=?, SortTitle=?, ContentRatingID=?  \
        WHERE ID=?', (title, plot, rating, month, days_since, year, tmdb_id, website,  \
        sorttitle, crating, file_id,))
        db.execute('DELETE FROM MGOAlbumArtistRelationship WHERE FileID=?', (file_id,))
        mgenlog = 'Mezzmo metadata MGOfile updates complete.'
        genLog(mgenlog, 'yes')

        if genrelist != None and len(genrelist) > 0:       # Genre table updates
            db.execute('DELETE FROM MGOFileGenreRelationship WHERE FileID=?', (file_id,))
            for genre in genrelist:
                #print('Checking genre: ' + genre)
                dccurr = db.execute('SELECT ID FROM MGOFileGenre WHERE Data=?', (genre,))
                dctuple = dccurr.fetchone()
                del dccurr
                if dctuple:
                    db.execute('INSERT into MGOFileGenreRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dctuple[0],))
                else:
                    mgenlog = 'Mezzmo genre not found in MGOFileGenre: ' + genre
                    genLog(mgenlog, 'yes')
            mgenlog = 'Mezzmo metadata genre updates complete.'
            genLog(mgenlog, 'yes')
        else:
            mgenlog = 'TMDB genrelist empty.  No Mezzmo genre updates to process.'
            genLog(mgenlog, 'yes') 

        if actorlist != None and len(actorlist) > 0:       # Actor tables updates
            #print(actorlist)
            db.execute('DELETE FROM MGOFileArtistRelationship WHERE FileID=?', (file_id,))
            for actors in actorlist:
                actor = actors[0]                          # Parse name from list of lists
                #print('Checking actor: ' + actor)
                dacurr = db.execute('SELECT ID FROM MGOFileArtist WHERE Data=?', (actor,))
                datuple = dacurr.fetchone()
                del dacurr
                if datuple:
                    db.execute('INSERT into MGOFileArtistRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, datuple[0],))
                else:
                    db.execute('INSERT into MGOFileArtist (Data) values (?)', (actor,))
                    mgenlog = 'Mezzmo actor not found and added to in MGOFileArtist: ' + actor
                    genLog(mgenlog, 'yes')
                    dacurr = db.execute('SELECT ID FROM MGOFileArtist WHERE Data=?', (actor,))
                    datuple = dacurr.fetchone()
                    del dacurr                                      
                    db.execute('INSERT into MGOFileArtistRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, datuple[0],))
            mgenlog = 'Mezzmo metadata actor updates complete.'
            genLog(mgenlog, 'yes')
        else:
            mgenlog = 'TMDB actorlist empty.  No Mezzmo actor updates to process.'
            genLog(mgenlog, 'yes')

        if studiolist != None and len(studiolist) > 0:       # Studio tables updates
            db.execute('DELETE FROM MGOFileProductionCompanyRelationship WHERE FileID=?', (file_id,))
            for studio in studiolist:
                #print('Checking studio: ' + studio)
                dscurr = db.execute('SELECT ID FROM MGOFileProductionCompany WHERE Data=?', (studio,))
                dstuple = dscurr.fetchone()
                del dscurr
                if dstuple:
                    db.execute('INSERT into MGOFileProductionCompanyRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dstuple[0],))
                else:
                    db.execute('INSERT into MGOFileProductionCompany (Data) values (?)', (studio,))
                    mgenlog = 'Mezzmo studio not found and added to in MGOFileProductionCompany: ' + studio
                    genLog(mgenlog, 'yes')
                    dscurr = db.execute('SELECT ID FROM MGOFileProductionCompany WHERE Data=?', (studio,))
                    dstuple = dscurr.fetchone()
                    del dscurr                                      
                    db.execute('INSERT into MGOFileProductionCompanyRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dstuple[0],))
            mgenlog = 'Mezzmo metadata studio updates complete.'
            genLog(mgenlog, 'yes')
        else:
            mgenlog = 'TMDB studiolist empty.  No Mezzmo studio updates to process.'
            genLog(mgenlog, 'yes')   
  
        if writerlist != None and len(writerlist) > 0:       # Writer tables updates
            db.execute('DELETE FROM MGOFileWriterRelationship WHERE FileID=?', (file_id,))
            for writer in writerlist:
                #print('Checking writer: ' + writer)
                dwcurr = db.execute('SELECT ID FROM MGOFileWriter WHERE Data=?', (writer,))
                dwtuple = dwcurr.fetchone()
                del dwcurr
                if dwtuple:
                    db.execute('INSERT into MGOFileWriterRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dwtuple[0],))
                else:
                    db.execute('INSERT into MGOFileWriter (Data) values (?)', (writer,))
                    mgenlog = 'Mezzmo writer not found and added to in MGOFileWriter: ' + writer
                    genLog(mgenlog, 'yes')
                    dwcurr = db.execute('SELECT ID FROM MGOFileWriter WHERE Data=?', (writer,))
                    dwtuple = dwcurr.fetchone()
                    del dwcurr                                      
                    db.execute('INSERT into MGOFileWriterRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dwtuple[0],))
            mgenlog = 'Mezzmo metadata writer updates complete.'
            genLog(mgenlog, 'yes')
        else:
            mgenlog = 'TMDB writerlist empty.  No Mezzmo writer updates to process.'
            genLog(mgenlog, 'yes')           

        if directorlist != None and len(directorlist) > 0:       # Director tables updates
            db.execute('DELETE FROM MGOFileCreatorRelationship WHERE FileID=?', (file_id,))
            for director in directorlist:
                #print('Checking director: ' + director)
                ddcurr = db.execute('SELECT ID FROM MGOFileCreator WHERE Data=?', (director,))
                ddtuple = ddcurr.fetchone()
                del ddcurr
                if ddtuple:
                    db.execute('INSERT into MGOFileCreatorRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, ddtuple[0],))
                else:
                    db.execute('INSERT into MGOFileCreator (Data) values (?)', (director,))
                    mgenlog = 'Mezzmo director not found and added to in MGOFileCreator: ' + director
                    genLog(mgenlog, 'yes')
                    ddcurr = db.execute('SELECT ID FROM MGOFileCreator WHERE Data=?', (director,))
                    ddtuple = ddcurr.fetchone()
                    del ddcurr                                      
                    db.execute('INSERT into MGOFileCreatorRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, ddtuple[0],))
            mgenlog = 'Mezzmo metadata director updates complete.'
            genLog(mgenlog, 'yes')
        else:
            mgenlog = 'TMDB directorlist empty.  No Mezzmo director updates to process.'
            genLog(mgenlog, 'yes')           

        if producerlist != None and len(producerlist) > 0:       # Producer tables updates
            db.execute('DELETE FROM MGOFileProducerRelationship WHERE FileID=?', (file_id,))
            for producer in producerlist:
                #print('Checking producer: ' + producer)
                dpcurr = db.execute('SELECT ID FROM MGOFileProducer WHERE Data=?', (producer,))
                dptuple = dpcurr.fetchone()
                del dpcurr
                if dptuple:
                    db.execute('INSERT into MGOFileProducerRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dptuple[0],))
                else:
                    db.execute('INSERT into MGOFileProducer (Data) values (?)', (producer,))
                    mgenlog = 'Mezzmo producer not found and added to in MGOFileProducer: ' + producer
                    genLog(mgenlog, 'yes')
                    dpcurr = db.execute('SELECT ID FROM MGOFileProducer WHERE Data=?', (producer,))
                    dptuple = dpcurr.fetchone()
                    del dpcurr                                      
                    db.execute('INSERT into MGOFileProducerRelationship (FileID, ID)     \
                    values (?, ?)', (file_id, dptuple[0],))
            mgenlog = 'Mezzmo metadata producer updates complete.'
            genLog(mgenlog, 'yes')
        else:
            mgenlog = 'TMDB producerlist empty.  No Mezzmo producer updates to process.'
            genLog(mgenlog, 'yes')           

        db.commit()
        db.close()
        time.sleep(0.1)

        mgenlog = 'Mezzmo metadata successfully updated.'
        genLog(mgenlog, 'yes')
        
    except Exception as e:
        print (e)
        fileh.close()
        mgenlog = ' There was an error updating Mezzmo metdata.'
        genLog(mgenlog, 'Yes')
        db.close()


def getTvUserPosterFiles(path):

    try:
        mgenlog = "Getting Mezzmo TV Show UserPoster files."
        genLog(mgenlog, 'Yes')   
        actdb = openActorDB()
        userposter = path + "UserPoster\\"   
        #print (userposter)
        listOfFiles = os.listdir(userposter)
        fcount = len(listOfFiles)  
        listOfFiles = str(listOfFiles).lower()
        listOfFiles2 = os.listdir(".\\UserPoster")
        fcount += len(listOfFiles2)
        listOfFiles2 = str(listOfFiles2).lower()
        listOfFiles += ","
        listOfFiles += listOfFiles2

        mgenlog = 'Number of actor artwork files in local and remote userposter folders: ' + str(fcount) 
        genLog(mgenlog, 'yes')

        #pattern = "*.jpg"
        #print(listOfFiles)
        return(listOfFiles)
    except Exception as e:
        print (e)
        return 0
        pass
        

def nameConvert(actor_name):                   # Remove unicode characters from userposter names

    try:
        if isinstance(actor_name, str):
            return unidecode(actor_name)
        else:
            return actor_name
    except Exception as e:
        print (e)
        return actor_name
        pass        


def getActorImage(url, actor, image_size):     # Get actor image file and save to userposter folder
  
        outfile = 'UserPoster\\' + actor + '.jpg'
        imagefile = 'https://image.tmdb.org/t/p/'  + image_size + url
        #print(imagefile)
        resource = urllib.request.urlopen(imagefile)
        output = open(outfile,"wb")
        output.write(resource.read())
        output.close()
        mgenlog = outfile + ' actor artwork file fetched from TMDB. '
        genLog(mgenlog, 'yes')


def json_print(data):                          # Print JSON data in readable format

    print(json.dumps(data, indent=4))
    input('Print Enter to continue')


    