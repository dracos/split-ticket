import itertools
import json
import os
import re
import sys
import urllib

from bottle import route, run, view

from split import dijkstra, fares, utils

# Load data
data_files = [ 'restrictions', 'stations', 'fares', 'routes', 'clusters' ]
data = {}
for d in data_files:
    with open(os.path.join(os.path.dirname(__file__), 'data', d + '.json')) as fp:
        data[d] = json.load(fp)

def find_stopping_points(store):
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
        print "Could not get stops"
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
    return all_stops

def find_cheapest(store):
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
    return nodes

@route('/')
def home():
    return 'Home page'

@route('/<fr>/<to>/<day>/<time>')
@view('result')
def split(fr, to, day, time):
    day = day == 'y'
    context = {
        'fr': fr,
        'to': to,
        'day': day,
        'time': time,
    }
    store = {
        'data': {},
        'station_times': {},
        'from': urllib.quote(fr),
        'to': urllib.quote(to),
        'day': day,
        'time': time,
    }

    store['station_times'][store['from']] = [ None, store['time'] ]
    all_stops = find_stopping_points(store)
    context['all_stops_with_depart'] = [ '%s(%s)' % (s, store['station_times'][s][1] or store['station_times'][s][0]) for s in all_stops ]

    stop_pairs = itertools.combinations(all_stops, 2)
    stop_pairs = filter(lambda x: x[0] != store['from'] or x[1] != store['to'], stop_pairs)
    Fares = fares.Fares(store, data)
    routes = {}
    fare_total = Fares.parse_fare(store['from'], store['to'])
    context['fare_total'] = fare_total
    if fare_total != '-':
        d = store['data'][store['from']][store['to']]
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']['name']
            routes[n] = { 'name': 'Exclude %s' % n, 'value': n }

    output_pairwise = []
    for pair in stop_pairs:
        out = Fares.parse_fare(pair[0], pair[1])
        times = ','.join(map(lambda x: x or '', store['station_times'][pair[0]]))
        output_pairwise.append( (pair[0], pair[1], times, out) )
    context['output_pairwise'] = output_pairwise

    nodes = find_cheapest(store)
    total = 0
    output_cheapest = []
    for i in range(0, len(nodes)-1):
        f = nodes[i]
        t = nodes[i+1]
        d = store['data'][f][t]
        output_cheapest.append( (f,t,d) )
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']['name']
            routes[n] = { 'name': 'Exclude %s' % n, 'value': n }
        total += d['fare']
    context['output_cheapest'] = output_cheapest
    context['total'] = total

    context['routes'] = routes
    return context
    #Fares.excluded_routes.append(answer['action'])

run(host='localhost', port=8080, debug=True)


