split.traintimes.org.uk
=======================

This app calculates split ticket possibilities. It is running at
http://split.traintimes.org.uk/ but should run locally without much issue.

Requirements
------------

* redis, for the queueing and front page latest.
* python
* virtualenv unless you like installing things system-wide, in which case you
  should know what you’re doing

Installation
------------

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

I used bower to install the JavaScript required, so you can either install
bower and then run bower install, or if that’s too much effort stick
http://split.traintimes.org.uk/bower_components/jquery/dist/jquery.min.js in
bower_components/jquery/dist/ and
http://split.traintimes.org.uk/bower_components/devbridge-autocomplete/dist/jquery.autocomplete.min.js
in bower_components/devbridge-autocomplete/dist/ :)

web.py is the WSGI application, you can run this directly with:

    python web.py

Which will start up a web server running on port 8080 by default. You can run
it via your favourite tool for doing so (I’m using gunicorn, behind
nginx and varnish).

You start a backend worker with:

    python worker.py

(I’m running multiple ones via supervisor, there is an example config.)
And you can monitor the workers with rqinfo.

Updating data
-------------

Get some fares and timetable data from http://data.atoc.org/ and unzip each
into their own directories, called fares-data-NNN and timetable-data-NNN (with
NNN being their respective ID).

Run:

    parse-tocs <fares-directory>
    parse-stations <fares-directory>
    parse-restrictions <fares-directory>
    parse-fares <fares-directory>
    parse-ndf <fares-directory>
    parse-trains <fares-directory> <timetable-directory>
    merge-fares-ndf <fares-directory>

And that should update all the JSON files.
