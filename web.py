import itertools
import json
import os
import re
import sys
import urllib

import bottle
from bottle import request

def alpha(user, pw):
    return user == 'train' and pw == 'choochoo'

from split import fares, utils, times

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

# Load data
data_files = [ 'restrictions', 'stations', 'routes', 'clusters' ]
data = {}
for d in data_files:
    with open(os.path.join(THIS_DIR, 'data', d + '.json')) as fp:
        data[d] = json.load(fp)

@bottle.route('/bower/<path:path>')
def server_static(path):
        return bottle.static_file(path, root=os.path.join(THIS_DIR, 'bower_components'))

@bottle.route('/ajax-station')
def ajax():
    q = request.query.q.lower()
    matches = filter(lambda x: q in x.lower(), data['stations'])
    matches += filter(lambda x: x not in matches and data['stations'][x]['description'].lower().startswith(q), data['stations'])
    matches += filter(lambda x: x not in matches and q in data['stations'][x]['description'].lower(), data['stations'])
    return {
        'results': [ { 'id': m, 'text': data['stations'][m]['description'] } for m in matches ]
    }

@bottle.route('/')
@bottle.auth_basic(alpha)
def home():
    if all(x in request.query and request.query[x] for x in ['from', 'to', 'time']):
        request.query['day'] = request.query.get('day') or 'n'
        bottle.redirect('/%(from)s/%(to)s/%(day)s/%(time)s' % request.query)
    return form(request.query)

@bottle.view('home')
def form(context):
    if 'from' in context and context['from'] in data['stations']:
        context['from_desc'] = data['stations'][context['from']]['description']
    if 'to' in context and context['to'] in data['stations']:
        context['to_desc'] = data['stations'][context['to']]['description']
    return context

@bottle.route('/<fr>/<to>/<day>/<time>')
@bottle.auth_basic(alpha)
@bottle.view('result')
def split(fr, to, day, time):
    if fr != fr.upper() or to != to.upper() or not re.match('^\d\d:\d\d', time):
        return form({ 'from': fr, 'to': to, 'day': day, 'time': time })

    day = day == 'y'
    context = {
        'fr': fr, 'fr_desc': data['stations'][fr]['description'],
        'to': to, 'to_desc': data['stations'][to]['description'],
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
    context['all_stops_with_depart'] = [ (s, data['stations'].get(s, { 'description': s }), store['station_times'][s]) for s in all_stops ]

    stop_pairs = itertools.combinations(all_stops, 2)
    stop_pairs = filter(lambda x: x[0] != store['from'] or x[1] != store['to'], stop_pairs)
    Fares = fares.Fares(store, data)

    context['exclude'] = filter(None, request.query.exclude.split(','))
    for route in context['exclude']:
        Fares.excluded_routes.append(route)

    routes = {}
    fare_total = Fares.parse_fare(store['from'], store['to'])
    context['fare_total'] = fare_total
    if fare_total['fare'] != '-':
        d = store['data'][store['from']][store['to']]
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']
            routes[n['id']] = { 'name': n['name'], 'value': n['id'] }

    output_pairwise = []
    for pair in stop_pairs:
        out = Fares.parse_fare(pair[0], pair[1])
        output_pairwise.append( (pair[0], pair[1], out) )
    context['output_pairwise'] = output_pairwise

    nodes, total = Fares.find_cheapest()
    output_cheapest = []
    for f, t, d in nodes:
        output_cheapest.append( (
            data['stations'][f]['description'],
            data['stations'][t]['description'], d
        ) )
        if d['obj']['route']['name'] != 'ANY PERMITTED':
            n = d['obj']['route']
            routes[n['id']] = { 'name': n['name'], 'value': n['id'] }
    context['output_cheapest'] = output_cheapest
    context['total'] = total

    context['routes'] = routes
    return context

if __name__ == "__main__":
    bottle.run(host='localhost', port=8080, debug=True, reloader=True)
app = bottle.default_app()
