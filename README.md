# Mezzmo Artwork Checker
A utility to help you manage your Mezzmo actor / actress artwork files.  


## Features:

- Pulls an actor listing from Mezzmo and normalizes it for comparison to poster and UserPoster
- Inserts Mezzmo actor records and normalized records into actorArtwork table
- Pulls UserPoster listing and inserts file into userPosterFile table
- Updates Mezzmo actorArtwork table if there is a UserPoster file match
- Pulls Poster listing and inserts file posterFile table
- Updates Mezzmo actorArtwork table if there is a Poster file match
- CSV export option
<br/>

## Installation and usage:

-  Download the Mezzmo Artwork Checker zipfile
-  Unzip file into an empty folder on your system
-  Ensure you have Python installed
-  Edit the config.text file with the location of your Mezzmo
   database and artwork
-  Open a command window (if Windows) and run mezzmo_actor.py
   See optional command line arguments below.  
   No arguments runs the actor artwork checker normally
<br/>

## Command line arguments:  (Limit 1 at a time)

- <b>clean</b>	-  Clears all table records in the mezzmo_artwork.db database
- <b>csv</b>    -  Runs the Mezzmo Artwork checker normallly but also outputs<br/> 
         the actorArtwork table to a CSV file actorartwork.csv  .
         
 The CSV export utility currently requires Python version 3 or higher.<br/><br/>

           
<br/><img src="icon.png" width="40%">
