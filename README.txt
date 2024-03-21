v1.0.16a

- Initial NFO feature test release

v1.0.16

- Changed last time checker ran output to just hh:mm:ss and dropped the partial secs
- Updated IMDB-API to TV-API URL change

v1.0.15

- Fixed a bug which would cause a divide by zero error when parsing the statistics
  and no IMDB fetch attempts occurred
- Fixed a statistics display bug where the TMDB fetched image counter would increment
  when it was skipped due to already being fetched by IMDB
- Added a daily new image counter to the display statistics so you can see new images
  added during the current day

v1.0.14

- Fixed bug with IMDB key parsing

v1.0.13

- Fixed issue fetching IMDB images due to an IMDB API change implemented on
  1/1/2023.   

v1.0.12

- Fixed IMDB rate calculation

v1.0.11

- Changed retry setting to be per actor / actress based vs. session based to
  improve image retrieval success rate when IMDB is busy. 
- Added IMDB query success rate calculation to quickly see how busy IMDB is
  for a retrieval session.      

v1.0.10

- Added retry setting in the configuration file for IMDB.  Previously the 
  default would be to stop fetching images after 3 consecutive failures.  The
  new default is 5 retries and can be set as high as 10.   

v1.0.9

- Added "noactor" command line option which will provide the Mezzmo data
  (i.e. movie title and file name) for any actor / actress which isn't found
  on IMDB and TMDB.  These are typically typos, improper spellings, other
  name variations and similar.  Actors deleted from Mezzmo are not included
  in the CSV file.

v1.0.8

- Fixed issue where images for actors deleted from Mezzmo were still being
  fetched from TMDB / IMDB.
- Improved current run counters to show number of queries requested vs. 
  number attempted.
- Added statistics to show Mezzmo actors not found on TMDB/IMDB.  These are
  often typos and bad data from TMDB/IMDB for specific movies / episodes.
 
v1.0.7

- Fixed issue where newly added Mezzmo actors would get marked deleted on
  the first run of the Mezzmo Artwork checker after being added and then 
  added on the second run.  Now new Mezzmo actors are first to be queued 
  for missing artwork.
- Added statistics for the current run of the Mezzmo Artwork Checker, in 
  addition to the overall statistics.  The current run statistics will be
  shown fist.
- Added an images command line option to override the config.txt settings
  for TMDB / IMDB query count.  Now you can specify how many actor to query
  on the command line.  Otherwise the Mezzmo artwork checker will use the 
  config file values.
 
  Example command:  mezzmo_actor.py images 100   (100 actor image query)    


v1.0.6

- Added detection and marking of actors / actresses which have been removed
  from the Mezzmo database.  They will be marked deleted in the actorArtwork
  table mezzmoChecked column but they will not be deleted from the table.  If
  they are later added again to Mezzmo, they will be detected.  Mezzmo deletions
  will be seen in the statistics display at the end.  You can get the specific
  details with a CSV export.
- Image fetching for TMDB and IMDB will no longer check for images which are
  already found on Mezzmo.  This will reduce the time required to cycle through
  missing images.
- Increased the maximum TMDB / IMDB config file query counts from 500 to 1000.
- Added an IMDB server busy detector to stop fetching after 3 consecutive server
  busy responses. 
- Minor cosmetic improvements with error messages and the statistics display.

v1.0.5

- Added TMDB image fetching.  The Mezzmo Addon Checker will check for missing
  artwork at TMDB first and if not found will then check IMDB if an IMDB API
  key has been entered in the config.txt file.  IMDB checking requires an 
  IMDB API Key which is available at:  https://imdb-api.com/pricing
  The first 100 IMDB checks per day can be done with a free key.  TMDB image
  checking is free with the already supplied key in the config.txt file. 
  ***  Do not modify the TMDB API Key information.  *** 
- Added checking for existing images in the IMDB and TMDB folders. If an actor
  / actress image file exists (i.e. hasn't been copied to the Mezzmo UserPoster
  folder yet) it will be detected and skipped vs. being overwritten.
- Improved IMDB artwork matching for records futher down in the IMDB API response 
- Made all command line arguments case insensitive
- Bad image option can now include file extension or not.  (i.e. john-doe or 
  john-doe.jpg are both good and case insensitive too.)
- Added statistics display at the end of running the Mezzmo Artwork checker.  The
  stats are a way to gain quick insight without running a CSV export.  
- Added UserPoster match "no" status rechecking to see if file pointing to no
  Mezzmo actor was removed / renamed.  

v1.0.4

- Improved IMDB error checking when actor / actress does not exist / not found.
- Fixed IMDB image fetching failures with non-ASCII characters in actor names
- Added new command line option: "bad" followed by the bad actor file name to
  indicate the image from IMDB is bad and to not download it again.  

  Example command:  mezzmo_actor.py bad john-doe 

  This will mark john-doe as a bad image and will not attempt to download again
  unless mezzmo_actor.py clean is run to clear the Mezzmo Actor database.  This
  feature is handy when IMDB has a bad image that you don't like for an actor.
- Added skipping IMDB image fetching for a actor / actress where a valid image 
  file is already on your Mezzmo server or has already been fetched from IMDB.
- Improved IMDB server error detection for server busy and invalid API key
- Fixed Poster and UserPoster image file information updating after initial 
  record insertion into the posterFile and userPosterFile tables.  

v1.0.3

-  Added last checked tracking and status to the actorArtwork table.  You can now
   see the last time am actor was checked and the status of the image file.
-  Added IMDB actor image fetching with command line option "images".  The "images"
   option will attempt to fetch properly sized actor / actress images from IMDB,
   will name them for the UserPoster file name format and will save them in a folder
   called IMDB for review, prior to copying to the UserPoster folder. You can also
   limit the number of images fetched each time in the configuration file.  The 
   default is 30 and the maximum is 500. 

   ***  Note the "images" feature requires a valid IMBD API Key in the configuration 
   file.  You can get an IMDB API Key at:  https://imdb-api.com/pricing  
   You can register for a free key which will allow up to 100 images a day. *** 

v1.0.2

-  Added an actor no match file output for CSV exports.  This CSV file will contain
   a listing of all actors / actresses which do not have a Poster or UserPoster 
   artwork file.
-  Changed CSV output file names by appending the hour/minute/second that the CSV 
   export was done.  This will allow keeping of CSV files for historical purposes
   vs. over writing them each time.

v1.0.1

-  Fixed performance issue with Poster file scanning due to missing database index
-  Changed poster and UserPoster scanning to look for additions during scan vs.
   deleting all files and adding them during scanning
-  actorArtwork dateAdded field is now the last time the record was updated or
   the date/time the Mezzmo actor was added, if no updates have occurred.

v1.0 - Initial release


