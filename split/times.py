import re

from . import utils

def find_stopping_points(store):
    stops = utils.fetch('http://traintimes.org.uk/' + store['from'] + '/' + store['to'] + '/' + store['time'] + '/next+tuesday')
    m = re.search('<li id="result0">[\s\S]*?<li id="result1">', stops)
    if m:
        res1 = m.group()
        m = re.search('<strong>.*?(\d\d:\d\d) &ndash; (\d\d:\d\d)', res1)
        if m:
            store['station_times'][store['from']] = [ None, m.group(1) ]
            store['station_times'][store['to']] = [ m.group(2), None ]
        m = re.findall('<td>(\d\d:\d\d)</td>\s*<td class="origin">.*?<abbr>([A-Z]{3})[\s\S]*?<td class="destination">.*?<abbr>([A-Z]{3})[\s\S]*?<td>(\d\d:\d\d)', res1)
        for q in m:
            if q[2] not in store['station_times']: store['station_times'][q[2]] = [ None, None ]
            store['station_times'][q[2]][0] = q[3]
            if q[1] not in store['station_times']: store['station_times'][q[1]] = [ None, None ]
            store['station_times'][q[1]][1] = q[0]

    m = re.search('<a[^>]*href="(/ajax-stoppingpoints[^"]*)">stops(?i)', stops)
    if not m:
        raise Exception, 'Could not get stops'

    ints = utils.fetch('http://traintimes.org.uk' + m.group(1).replace('stage=', '') + ';ajax=2')
    stops = []
    c = 0

    for x in ints['tables']:
        op = ints['operators'][c]
        stops += map(lambda x: (x, False, op), re.findall('<abbr>([A-Z]{3})', x))
        stops.append( (re.search('[A-Z]{3}', ints['destination'][c]).group(), True, op) )
        c += 1

    for i in ints['parsed']:
        store['station_times'][i] = ints['parsed'][i]

    all_stops = [ (store['from'], True, None) ] + stops
    return all_stops
