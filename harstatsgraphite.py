#!/usr/bin/env python

import sys
import json
import time
import collections

if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


media_mime = (
    'image/',
    'video/',
    'audio/',
    'application/x-shockwave-flash',
    'font/',
    )

text_mime = (
    'application/x-javascript',
    'application/javascript',
    'application/xml',
    'application/json',
    'text/',
    )


# isodate and dateutil are a bit of an overkill
def mktimeISO8601(s):
    sec, msec = s.split('.', 1)

    sec = time.strptime(sec, "%Y-%m-%dT%H:%M:%S")
    sec = time.mktime(sec)

    if '+' in msec: msec = msec.split('+', 1)[0]
    elif '-' in msec: msec = msec.split('-', 1)[0]
    msec = msec.replace('Z', '')

    return sec + float('0.%s' % msec)


# convert datetimes and urls while parsing json
def jsondecode(el):
    if 'url' in el:
        el['url'] = urlparse(el['url'])
    if 'startedDateTime' in el:
        el['startedDateTime'] = mktimeISO8601(el['startedDateTime'])

    return el
    

def ismedia(entry):
    mtype = entry['response']['content']['mimeType'].split(';')[0]
    for m in media_mime:
        if mtype.startswith(m): return True
    return False


def istext(entry):
    mtype = entry['response']['content']['mimeType'].split(';')[0]
    for m in text_mime:
        if mtype.startswith(m):
            return True
    return False


def entry_counts(entry, c, k):
    c[k + 'count.total'] += 1

    c[k + 'count.media'] += 1 if ismedia(entry) else 0
    c[k + 'count.text']  += 1 if istext(entry) else 0

    c[k + 'time.dns']      += entry['timings']['dns']
    c[k + 'time.transfer'] += entry['timings']['receive'] + \
                              entry['timings']['send']

    c[k + 'time.receive']  += entry['timings']['receive']
    c[k + 'time.send']     += entry['timings']['send']
    c[k + 'time.wait']     += entry['timings']['wait']
    c[k + 'time.connect']  += entry['timings']['connect']
    c[k + 'time.blocked']  += entry['timings']['blocked']


# @bug: wrong hierarchy
def entry_sizes(entry, c, k):
    c[k + 'response.headers'] += entry['response']['headersSize']
    c[k + 'response.bodies'] += entry['response']['bodySize']
    c[k + 'request.headers'] += entry['request']['headersSize']
    c[k + 'request.bodies'] += entry['request']['bodySize']
    c[k + 'content'] += entry['response']['content']['size']


def parsehar(fn):
    # @todo: gzip support for python 3.2
    if fn.endswith('.gz'):
        import gzip
        if sys.version_info >= (3, 0):
            import functools
            open_cb = functools.partial(gzip.open, encoding='utf8')
        else:
            open_cb = gzip.open
    else:
        open_cb = open

    # parse (possibly gzipped) json 
    with open_cb(fn) as fh:
        # we don't want to deal with negative numbers
        parseint = lambda x: max(int(x), 0)
        data = json.load(fh, object_hook=jsondecode, parse_int=parseint)

    return data


def summarize(data, local=None):
    counts = c = collections.defaultdict(int)
    domains = set()

    timestamp_min = 2e9  
    timestamp_max = 0

    first_entry = None

    for entry in data['log']['entries']:
        url = entry['request']['url']
        netloc, path = url.netloc, url.path

        # find the earliest request
        started = entry['startedDateTime']
        finished = started + entry['time']/1000.

        if finished > timestamp_max:
            timestamp_max = finished

        if started < timestamp_min:
            timestamp_min = started
            first_entry = entry

        if local:
            if netloc == local:
                entry_counts(entry, c, 'requests.local.')
            else:
                entry_counts(entry, c, 'requests.external.')

        entry_counts(entry, c, 'requests.')
        entry_sizes(entry, c, 'transfer.')

        if ismedia(entry):
            entry_sizes(entry, c, 'requests.media.')
        elif istext(entry):
            entry_sizes(entry, c, 'requests.text.')

        status = entry['response']['status']
        c['status.redirect'] = 0
        c['status.bad'] = 0
        if 400 > status >= 300:
            c['status.redirect'] += 1
        if status >= 400:
            c['status.bad'] += 1

        # total number of network requests
        domains.add(netloc)

    if first_entry:
        c['requests.time.firstrequest'] += \
            first_entry['timings']['blocked'] + \
            first_entry['timings']['dns'] + \
            first_entry['timings']['connect'] + \
            first_entry['timings']['send'] + \
            first_entry['timings']['wait']

    c['requests.domains.count'] = len(domains)
    c['page.time.onLoad'] = data['log']['pages'][0]['pageTimings']['onLoad']
    c['page.time.onContentLoad'] = data['log']['pages'][0]['pageTimings']['onContentLoad']

    return counts

def serialize(counts, format='plain', prefix='har.summary', timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())
    
    # carbon pickle protocol
    if format == 'pickle':
        from pickle import dumps
        from struct import pack

        items = []
        for key, stat in sorted(counts.items()):
            items.append( (key, (timestamp, stat)) )

        payload = dumps(items, -1)
        header = pack('!L', len(payload))
        message = header + payload

        return message

    # carbon line protocol
    if format == 'plain':
        lines = []
        for key, stat in sorted(counts.items()):
            lines.append('%s.%s %s %s' % (prefix, key, stat, timestamp))
        return '\n'.join(lines)


if __name__ == '__main__':
    from getopt import getopt
    from textwrap import dedent

    usage = '''\
    Usage: python -m harstats_graphite [options] <harfile>

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

      har.summary.requests.external.count 92 1352934738
      har.summary.requests.local.count 28 1352934738
      har.summary.requests.count 120 1352934738'''

    # parse options and arguments
    longopts = ('help', 'local=', 'timestamp=', 'format=', 'path=')
    opts, args = getopt(sys.argv[1:], 'hl:t:f:p:', longopts)
    opts = dict(opts)

    if '-h' in opts or '--help' in opts or len(sys.argv) == 1:
        sys.stderr.write(dedent(usage) + '\n')
        sys.exit(1)

    timestamp = opts.get('-t') or opts.get('--timestamp') or time.time()
    prefix    = opts.get('-p') or opts.get('--prefix') or 'har.summary'
    format    = opts.get('-f') or opts.get('--format') or 'plain'
    local     = opts.get('-l') or opts.get('--local') 

    data = parsehar(args[0])
    counts = summarize(data, local)
    payload = serialize(counts, format, prefix, int(timestamp))

    fh = sys.stdout
    if sys.version_info >= (3, 0) and isinstance(payload, bytes):
        fh = sys.stdout.buffer

    fh.write(payload)
    fh.write('\n')


__all__ = 'summarize', 'serialize', 'parsehar'
