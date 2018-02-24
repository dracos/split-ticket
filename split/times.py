import re
import urllib

import requests

from . import utils
from .data import data

class Stop(object):
    def __init__(self, code, chg, op, times):
        self.code = code
        self.change = chg
        self.operator = op
        self.times = times
        try:
            self.desc = data['stations'][code]['description']
        except:
            self.desc = code

    def __repr__(self):
        return '%s %s %s %s' % (self.code, self.times, self.change, self.operator)

    def __eq__(self, other):
        return self.code == other.code

class Times(object):
    def __init__(self, stops, station_times):
        self.stops = []
        self.by_stop = {}
        for code, chg, op in stops:
            times = station_times.get(code)
            stop = Stop(code, chg, op, times)
            self.by_stop[code] = stop
            self.stops.append(stop)

    def __iter__(self):
        for stop in self.stops:
            yield(stop)

    def __len__(self):
        return len(self.stops)

    def __getitem__(self, stop):
        if isinstance(stop, int):
            return self.stops[stop]
        else:
            return self.by_stop[stop]

def find_stopping_points(context, ret=False):
    if ret:
        fr = context['to']
        to = context['from']
        time = context['time_ret']
    else:
        fr = context['from']
        to = context['to']
        time = context['time']

    station_times = {
        fr: [ None, time ]
    }
    url = 'https://traintimes.org.uk/' + urllib.quote(fr) + '/' + urllib.quote(to) + '/' + time
    if ret and context['day'] == 'n':
        url += '/next-wednesday'
    else:
        url += '/next-tuesday'
    if context['via']:
        url += '?via=' + urllib.quote(context['via'])
    if context.get('avoid'):
        url += '?avd=' + urllib.quote(context['avoid'])
    for i in range(0,2):
        stops = utils.fetch(url)
        if 'result0' in stops:
            break
        else:
            requests.Session().cache.delete_url(url)
    m = re.search('<li id="result0">[\s\S]*?(?:<li id="result1">|</ul>)', stops)
    if m:
        res1 = m.group()
        m = re.search('<strong>.*?(\d\d:\d\d) &ndash; (\d\d:\d\d)', res1)
        if m:
            station_times[fr] = [ None, m.group(1) ]
            station_times[to] = [ m.group(2), None ]
        m = re.findall('<td>(\d\d:\d\d)&ndash;(\d\d:\d\d)[\s\S]*?</td>\s*<td class="origin">.*?<abbr>([A-Z]{3})[\s\S]*?<td class="destination">.*?<abbr>([A-Z]{3})', res1)
        for q in m:
            if q[3] not in station_times: station_times[q[3]] = [ None, None ]
            station_times[q[3]][0] = q[1]
            if q[2] not in station_times: station_times[q[2]] = [ None, None ]
            station_times[q[2]][1] = q[0]

    m = re.search('<a[^>]*href="(/ajax-stoppingpoints[^"]*)">stops(?i)', stops)
    if not m:
        return None

    url = 'https://traintimes.org.uk' + m.group(1).replace('stage=', '') + ';ajax=2'
    for i in range(0,2):
        ints = utils.fetch(url)
        if ints['tables']:
            break
        else:
            requests.Session().cache.delete_url(url)

    stops = []
    c = 0

    for x in ints['tables']:
        op = ints['operators'][c]
        stops += map(lambda x: (x, False, op), re.findall('<abbr>([A-Z]{3})', x))
        stops.append( (re.search('[A-Z]{3}', ints['destination'][c]).group(), True, op) )
        c += 1

    for i in ints['parsed']:
        station_times[i] = ints['parsed'][i]

    all_stops = [ (fr, True, None) ] + stops

    return Times(all_stops, station_times)
