import itertools
import json
import os
import re
import sys
import urllib

from bottle import route, run, view

from split import fares, utils, times

# Load data
data_files = [ 'restrictions', 'stations', 'fares', 'routes', 'clusters' ]
data = {}
for d in data_files:
    with open(os.path.join(os.path.dirname(__file__), 'data', d + '.json')) as fp:
        data[d] = json.load(fp)

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
    all_stops = times.find_stopping_points(store)
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
        stop_times = ','.join(map(lambda x: x or '', store['station_times'][pair[0]]))
        output_pairwise.append( (pair[0], pair[1], stop_times, out) )
    context['output_pairwise'] = output_pairwise

    nodes, total = Fares.find_cheapest()
    output_cheapest = []
    for f, t, d in nodes:
        output_cheapest.append( (f,t,d) )
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']['name']
            routes[n] = { 'name': 'Exclude %s' % n, 'value': n }
    context['output_cheapest'] = output_cheapest
    context['total'] = total

    context['routes'] = routes
    return context
    #Fares.excluded_routes.append(answer['action'])

run(host='localhost', port=8080, debug=True)


