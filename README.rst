harstats-graphite
=================

This is a python module/script for parsing and summarizing `HTTP Archive (HAR)`_
files. Its output can be fed directly to `carbon`_'s line and pickle receivers.


Example Graphs
--------------

.. image::  https://github.com/gvalkov/screenshots/raw/master/thumb/harstats-graphite-01.png
   :target: https://github.com/gvalkov/screenshots/raw/master/full/harstats-graphite-01.png

.. image::  https://github.com/gvalkov/screenshots/raw/master/thumb/harstats-graphite-02.png
   :target: https://github.com/gvalkov/screenshots/raw/master/full/harstats-graphite-02.png

.. image::  https://github.com/gvalkov/screenshots/raw/master/thumb/harstats-graphite-03.png
   :target: https://github.com/gvalkov/screenshots/raw/master/full/harstats-graphite-03.png

.. image::  https://github.com/gvalkov/screenshots/raw/master/thumb/harstats-graphite-04.png
   :target: https://github.com/gvalkov/screenshots/raw/master/full/harstats-graphite-04.png


Example Output
--------------

::

    $ python -m harstatsgraphite /path/to/har.json 
    har.summary.page.time.onContentLoad 1917 1353082153
    har.summary.page.time.onLoad 3550 1353082153
    har.summary.requests.count.media 90 1353082153
    har.summary.requests.count.text 30 1353082153
    har.summary.requests.count.total 120 1353082153
    har.summary.requests.domains.count 22 1353082153
    har.summary.requests.media.content 1569613 1353082153
    har.summary.requests.media.request.bodies 0 1353082153
    har.summary.requests.media.request.headers 30509 1353082153
    har.summary.requests.media.response.bodies 1569613 1353082153
    har.summary.requests.media.response.headers 30360 1353082153
    har.summary.requests.text.content 838946 1353082153
    har.summary.requests.text.request.bodies 0 1353082153
    har.summary.requests.text.request.headers 11811 1353082153
    har.summary.requests.text.response.bodies 239329 1353082153
    har.summary.requests.text.response.headers 7040 1353082153
    har.summary.requests.time.blocked 9445 1353082153
    har.summary.requests.time.connect 1400 1353082153
    har.summary.requests.time.dns 19 1353082153
    har.summary.requests.time.firstrequest 123 1353082153
    har.summary.requests.time.receive 1367 1353082153
    har.summary.requests.time.send 0 1353082153
    har.summary.requests.time.transfer 1367 1353082153
    har.summary.requests.time.wait 5259 1353082153
    har.summary.status.bad 0 1353082153
    har.summary.status.redirect 0 1353082153
    har.summary.transfer.content 2408559 1353082153
    har.summary.transfer.request.bodies 0 1353082153
    har.summary.transfer.request.headers 42320 1353082153
    har.summary.transfer.response.bodies 1808942 1353082153
    har.summary.transfer.response.headers 37400 1353082153
    
    $ harstatsgraphite.py -l local.domain -p h -t 100 /path/to/har.json 
    h.page.time.onContentLoad 1917 100
    h.page.time.onLoad 3550 100
    h.requests.count.media 90 100
    h.requests.count.text 30 100
    h.requests.count.total 120 100
    h.requests.domains.count 22 100
    h.requests.external.count.media 88 100
    h.requests.external.count.text 4 100
    h.requests.external.count.total 92 100
    h.requests.external.time.blocked 8037 100
    h.requests.external.time.connect 150 100
    h.requests.external.time.dns 6 100
    h.requests.external.time.receive 1220 100
    h.requests.external.time.send 0 100
    h.requests.external.time.transfer 1220 100
    h.requests.external.time.wait 3210 100
    h.requests.local.count.media 2 100
    h.requests.local.count.text 26 100
    h.requests.local.count.total 28 100
    h.requests.local.time.blocked 1408 100
    h.requests.local.time.connect 1250 100
    h.requests.local.time.dns 13 100
    h.requests.local.time.receive 147 100
    h.requests.local.time.send 0 100
    h.requests.local.time.transfer 147 100
    h.requests.local.time.wait 2049 100
    h.requests.media.content 1569613 100
    h.requests.media.request.bodies 0 100
    h.requests.media.request.headers 30509 100
    h.requests.media.response.bodies 1569613 100
    h.requests.media.response.headers 30360 100
    h.requests.text.content 838946 100
    h.requests.text.request.bodies 0 100
    h.requests.text.request.headers 11811 100
    h.requests.text.response.bodies 239329 100
    h.requests.text.response.headers 7040 100
    h.requests.time.blocked 9445 100
    h.requests.time.connect 1400 100
    h.requests.time.dns 19 100
    h.requests.time.firstrequest 123 100
    h.requests.time.receive 1367 100
    h.requests.time.send 0 100
    h.requests.time.transfer 1367 100
    h.requests.time.wait 5259 100
    h.status.bad 0 100
    h.status.redirect 0 100
    h.transfer.content 2408559 100
    h.transfer.request.bodies 0 100
    h.transfer.request.headers 42320 100
    h.transfer.response.bodies 1808942 100
    h.transfer.response.headers 37400 100


Usage
-----

*harstatsgraphite.py* can be used programmatically or as a script::

   import harstatsgraphite as hs

   raw = hs.parsehar('path/to/harfile.json')
   data = hs.summarize(raw)
   print(hs.serialize(data))

::

   Usage: python -m harstatsgraphite [options] <harfile>

   Arguments:
     harfile                  path to HAR file (gzipped or plain)

   Options:
     -h, --help               show this help message and exit
     -l, --local <fqdn>       local domain name
     -t, --timestamp <sec>    timestamp to use (default: date +%s)
     -f, --format <arg>       plain or pickle (default: plain)
     -p, --prefix <arg>       metric prefix (default: har.summary)

   If the '-l --local' option is given, the script will split request
   statistics into three groups - requests to the local domain, all
   other domains and all requests. Example for 'requests.count':

     har.summary.requests.extern.count 92 1352934738
     har.summary.requests.local.count 28 1352934738
     har.summary.requests.count 120 1352934738'''

Installation
------------

*harstatsgraphite.py* has no dependencies outside of the Python
STL. It should work on Python `>=2.5 ∪ >=3.2`. Install with `pip` or
simply download it::

    $ pip install harstats-graphite
    $ curl -OL https://raw.github.com/gvalkov/harstats-graphite/master/harstatsgraphite.py

License
-------

*har-stats-graphite.py* is released under the terms of the New BSD License.


.. _`HTTP Archive (HAR)`: http://dvcs.w3.org/hg/webperf/raw-file/tip/specs/HAR/Overview.html
.. _`carbon`: https://graphite.readthedocs.org/en/latest/index.html
