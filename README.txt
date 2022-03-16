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


