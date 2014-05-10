#!/usr/bin/env python

import argparse
import itertools
import re
import urllib
import os, json

import codecs
import sys
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from termcolor import colored

from split import dijkstra, fares, prompt, utils

data_files = [ 'restrictions', 'stations', 'fares', 'routes', 'clusters' ]
data = {}
for d in data_files:
    with open(os.path.join(os.path.dirname(__file__), 'data', d + '.json')) as fp:
        data[d] = json.load(fp)

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

def verbose(s):
    if args.verbose:
        print colored(s, 'grey'),

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
from_stns = utils.fetch('http://api.brfares.com/ac_loc?term=' + urllib.quote(ans['from']))
to_stns = utils.fetch('http://api.brfares.com/ac_loc?term=' + urllib.quote(ans['to']))

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
# 2 Work out stopping points

verbose('Fetching stopping points...')

stops = utils.fetch('http://traintimes.org.uk/' + store['from'] + '/' + store['to'] + '/' + store['time'] + '/monday')
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

ints = utils.fetch('http://traintimes.org.uk' + m.group(1) + ';ajax=2')
stops = []
c = 0

for x in ints['tables']:
    stops += re.findall('<abbr>([A-Z]{3})', x)
    stops.append( re.search('[A-Z]{3}', ints['destination'][c]).group() )
    c += 1

for i in ints['parsed']:
    store['station_times'][i] = ints['parsed'][i]

all_stops = [ store['from'] ] + stops
all_stops_with_depart = [ '%s(%s)' % (s, store['station_times'][s][1] or store['station_times'][s][0]) for s in all_stops ]
print 'Stations to consider:', colored(', '.join(all_stops_with_depart), 'white', attrs=['dark'])

stop_pairs = itertools.combinations(all_stops, 2)
stop_pairs = filter(lambda x: x[0] != store['from'] or x[1] != store['to'], stop_pairs)

Fares = fares.Fares(store, data)

while True:
    routes = {}
    store['data'] = {}

    # ---
    # 3 Fare for entire journey

    verbose('Looking up journey as a whole...')
    fare_total = Fares.parse_fare(store['from'], store['to'])
    print 'Total fare is', colored(utils.price(fare_total['fare']), 'blue'), fare_total['desc']
    if fare_total['fare'] != '-':
        d = store['data'][store['from']][store['to']]
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']['name']
            routes[n] = { 'name': 'Exclude %s' % n, 'value': n }

    # ---
    # 4 Work out all possible intermediate fares

    verbose('Looking up all the pairwise fares...')
    for pair in stop_pairs:
        verbose(pair[0] + '-' + pair[1] + ' (')
        verbose(','.join(map(lambda x: x or '', store['station_times'][pair[0]])))
        verbose('):')
        out = Fares.parse_fare(pair[0], pair[1])
        verbose(utils.price(out['fare']) + ' ' + out['desc'] + "\n")

    # ---
    # 5 Work out cheapest route

    verbose('Calculating shortest route...')

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
        print f, colored('->', 'grey'), t, colored(':', 'grey'), utils.price(d['fare']), d['desc']
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']['name']
            routes[n] = { 'name': 'Exclude %s' % n, 'value': n }
        total += d['fare']
    print colored('Total: ' + utils.price(total), 'green')

    if not routes: sys.exit()
    qns = [ { 'type': "list", 'name': "action", 'message': "Action", 'choices': routes.values() } ]
    answer = prompt.pretty_prompt(qns)
    Fares.excluded_routes.append(answer['action'])
    print
