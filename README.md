# Mezzmo Artwork Checker
A utility to help you manage your Mezzmo actor / actress artwork files.  


<b>Features:</b>

- Pulls an actor listing from Mezzmo and normalizes it for comparison to poster and UserPoster
- Inserts Mezzmo actor records and normalized records into actorArtwork table
- Pulls UserPoster listing and inserts file into userPosterFile table
- Updates Mezzmo actorArtwork table if there is a UserPoster file match
- Pulls Poster listing and inserts file posterFile table
- Updates Mezzmo actorArtwork table if there is a Poster file match
- CSV export option


<b>Installation and usage:</b>

-  Download the Mezzmo Artwork Checker zipfile
-  Unzip file into an empty folder on your system
-  Ensure you have Python installed
-  Edit the config.text file with the location of your Mezzmo
   database and artwork
-  Open a command window (if Windows) and run mezzmo_actor.py
   See optional command line arguments below.  
   No arguments runs the actor artwork checker normally


<b>Command line arguments:  (Limit 1 at a time)</b>

clean	-  Clears all table records in the mezzmo_artwork.db database
csv	-  Runs the normal mezzmo_artwork checker but also outputs 
           the actorArtwork table to a CSV file actorartwork.csv
           The CSv export utility currently requires Python version 3
           or higher.

           
<img src="icon.png" width="40%">