# httpmp3ripper

mp3 ripping http proxy (hack!), by Sebastian Volland, based on Jonas Wagner's
[HTTPRipper](http://github.com/jwagner/httpripper).

## features

* commandline tool, no anoying gui
* acts as http proxy
* every file with mimetype _audio/mpeg_ is saved as .mp3 file in a directory
* filenames are constructed using their id3-tag (`00-artist-album.mp3` where 00 is the track number)
* if id3 tag contains no track number, the track number is automatically incremented for each song per album

## requirements

* python with id3lib (macports package py-id3lib), and probably some other libraries

tested on max osx 10.7.4 with macports. should work on linux and maybe also windows.

## instructions

* start server: `python httpmp3ripper.py 8080 /tmp/mp3` (where 8080 is the listen port and `/tmp/mp3` target path)
* set your system proxy to 127.0.0.1:8080
* press play/record/whatever in your app/website you want to intercept
* new mp3s are stored in target directory
* if you are done, press ctrl+c to stop the http proxy

