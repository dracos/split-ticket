#!/usr/bin/env python

from __future__ import division
import itertools
import json
import re
import urllib

import codecs
import sys
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import requests
import requests_cache
from termcolor import colored

from split import dijkstra, restrictions, prompt

requests_cache.install_cache('split', expires_after=86400)

def prettify(s):
    s = re.sub('\w\S*', lambda txt: txt.group().title(), s)
    s = re.sub(' R$', ' Return', s)
    s = re.sub(' S$', ' Single', s)
    return s

def Pfetch(url):
    r = requests.get(url)
    try:
        return r.json()
    except:
        return r.text

def price(n):
    return (u'\xa3%.2f' % (n/100)).replace('.00', '')

def parse_fare(fro, to):
    body = Pfetch('http://api.brfares.com/querysimple?orig=' + fro + '&dest=' + to)

    def fare_list(s):
        o = price(s['adult']['fare'])
        o += ' (' + prettify(s['ticket']['name'])
        if s['route']['name'] != 'ANY PERMITTED': o += ', ' + prettify(s['route']['name'])
        # if s['restriction_code'] != '  ': o += ', ' + s['restriction_code']
        o += ')'
        return o

    def match(s):
        ret = re.search('SVR|SOR', s['ticket']['code'])
        if store['day']:
            ret = ret or re.search('CDR|SDR', s['ticket']['code'])
        ret = ret and restrictions.valid_journey(
            fro, to, store['station_times'].get(fro), store['station_times'].get(to), s['restriction_code']
        )
        return ret
    returns = filter(match, body['fares'])

    best_per_route = {}
    best = None
    for r in returns:
        if not best or r['adult']['fare'] < best['adult']['fare']:
            best = r
        if r['route']['name'] not in best_per_route or r['adult']['fare'] < best_per_route[r['route']['name']]['adult']['fare']:
            best_per_route[r['route']['name']] = r

    double = False
    if best:
        print ' | '.join(map(fare_list, returns)) + ' ',
    else:
        def match(s):
            ret = re.search('CDS|SDS|SOS', s['ticket']['code'])
            ret = ret and restrictions.valid_journey(
                fro, to, store['station_times'].get(fro), store['station_times'].get(to), r['restriction_code']
            )
            return ret
        singles = filter(match, body['fares'])
        for r in singles:
            if not best or r['adult']['fare'] < best['adult']['fare']:
                best = r
        if best:
            print ' | '.join(map(fare_list, singles)) + ' ',
            double = true

    if not best:
        return '-'

    fare = best['adult']['fare'] * (2 if double else 1)
    if fro not in store['data']: store['data'][fro] = {}
    if to not in store['data']: store['data'][to] = {}
    store['data'][fro][to] = { 'fare': fare, 'desc': fare_list(best) }
    disp = price(fare)
    if double: disp += ' (2 singles)'
    return disp

# ---
# 0 Global data store

store = { 'data': {}, 'station_times': {} }

# ---
# 1 Get input

ans = prompt.pretty_prompt([
    { 'default': 'BRV', 'name': "from", 'message': "From", 'validate': lambda x: x },
    { 'default': 'RDG', 'name': "to", 'message': "To", 'validate': lambda x: x },
    { 'name': "day", 'message': "For the day", 'type': "confirm" },
    { 'name': "time", 'message': "Departure time", 'default': "08:02",
        'validate': lambda x: re.match('^\d\d:\d\d$', x)
    },
])

store['day'] = ans['day']
store['time'] = ans['time']
from_stns = Pfetch('http://api.brfares.com/ac_loc?term=' + urllib.quote(ans['from']))
to_stns = Pfetch('http://api.brfares.com/ac_loc?term=' + urllib.quote(ans['to']))

def modify(x):
    x['name'], x['value'] = x['value'], x['code']
    return x

from_stns = map(modify, from_stns)
to_stns = map(modify, to_stns)
if len(from_stns) > 1:
    qns = [ { 'type': "list", 'name': "from", 'message': "From choice", 'choices': from_stns, } ]
    from_stn = prompt.pretty_prompt(qns)
else:
    from_stn = { 'from': from_stns[0]['code'] }
if len(to_stns) > 1:
    qns = [ { 'type': "list", 'name': "to", 'message': "To choice", 'choices': to_stns, } ]
    to_stn = prompt.pretty_prompt(qns)
else:
    to_stn = { 'to': to_stns[0]['code'] }

store['from'] = urllib.quote(from_stn['from'])
store['to'] = urllib.quote(to_stn['to'])
store['station_times'][store['from']] = [ None, store['time'] ]

# ---
# 2 Fare for entire journey

print colored('Looking up journey as a whole...', 'grey')
fare_total = parse_fare(store['from'], store['to'])
print '\nTotal fare is', colored(fare_total, 'blue')

# ---
# 3 Work out stopping points

print colored('Fetching stopping points...', 'grey')

stops = Pfetch('http://traintimes.org.uk/' + store['from'] + '/' + store['to'] + '/' + store['time'] + '/monday')
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
    print colored("Could not get stops", 'red')
    sys.exit(1)

ints = Pfetch('http://traintimes.org.uk' + m.group(1) + ';ajax=2')
stops = []
c = 0

for x in ints['tables']:
    stops += re.findall('<abbr>([A-Z]{3})', x)
    stops.append( re.search('[A-Z]{3}', ints['destination'][c]).group() )
    c += 1

for i in ints['parsed']:
    store['station_times'][i] = ints['parsed'][i]

all_stops = [ store['from'] ] + stops
print 'Stations to consider:', colored(', '.join(all_stops), 'grey')

# ---
# 4 Work out all possible intermediate fares

print colored('Looking up all the pairwise fares...', 'grey')

stop_pairs = itertools.combinations(all_stops, 2)
stop_pairs = filter(lambda x: x[0] != store['from'] or x[1] != store['to'], stop_pairs)

for pair in stop_pairs:
    print colored(pair[0] + '-' + pair[1] + ' (', 'white', attrs=['dark']),
    print colored(','.join(map(lambda x: x or '', store['station_times'][pair[0]])), 'grey'),
    print colored('): ', 'white', attrs=['dark']),
    out = parse_fare(pair[0], pair[1])
    print colored(out, 'grey')

# ---
# 5 Work out cheapest route

print colored('Calculating shortest route...', 'grey')

graph = dijkstra.Graph()
for x in store['data'].keys():
    graph.add_node(x)

for x in store['data'].keys():
    for y in store['data'][x].keys():
        if store['data'][x][y]['fare'] != -1:
            graph.add_edge(x, y, store['data'][x][y]['fare'])

result, path = dijkstra.dijkstra(graph, store['from'])
node = store['to']
nodes = [];
while node:
    nodes.append(node)
    node = path.get(node)

nodes.reverse()
total = 0
for i in range(0, len(nodes)-1):
    f = nodes[i]
    t = nodes[i+1]
    d = store['data'][f][t]
    print f, colored('->', 'grey'), t, colored(':', 'grey'), d['desc']
    total += d['fare']
print colored('Total: ' + price(total), 'green')
