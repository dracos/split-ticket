import json
import os
import re

# Load data
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
data_files = [ 'trains' ]
data = {}
for d in data_files:
    with open(os.path.join(THIS_DIR, '..', 'data', d + '.json')) as fp:
        data[d] = json.load(fp)

def considered_stops(all_stops, fro, to):
    """Origin, destination, and anywhere we change"""
    stops = []
    started = False
    for stop, chg, op in all_stops:
        if stop == fro or stop == to:
            started = chg = True
        if started and chg:
            stops.append((stop, op))
        if stop == to:
            break
    return stops

def next_op(all_stops, stop):
    found = False
    for s in all_stops:
        if found == True:
            return s[2]
        if s[0] == stop:
            found = True

class Times(object):
    def __init__(self, station_times):
        self.station_times = station_times

    def get_time(self, s, dir):
        t = self.station_times[s][dir]
        if t: t = t.replace(':', '')
        return t

class Restriction(object):
    def __init__(self, restriction):
        self.restriction = restriction

    def lookup(self, s):
        resp = self.restriction.get(s, {})
        resp = [ v for k,v in resp.items() if not re.search('R$', k) ]
        return resp

def valid_journey(restrictions, fro, to, all_stops, station_times, code):
    if not code.strip(): return True

    times = Times(station_times)
    dep = times.get_time(fro, 1)
    arr = times.get_time(to, 0)

    if 'trains' in restrictions[code] and restrictions[code]['info']['type_out'] == 'P':
        trains = restrictions[code]['trains']
        trains = ( train['id'] for train in trains if train['dir'] == 'O' )
        trains = ( train for train in trains if train in data['trains'] )
        for train in trains:
            journey = data['trains'][train]['stops']
            if fro in journey and to in journey and journey[fro][1] == dep and journey[to][0] == arr:
                return True

    if 'times' in restrictions[code]:
        restriction = Restriction(restrictions[code]['times'])
        all_restriction = restriction.lookup("")
        for stop, op in considered_stops(all_stops, fro, to):
            op_next = next_op(all_stops, stop)
            stop_arr = times.get_time(stop, 0)
            stop_dep = times.get_time(stop, 1)
            for a in restriction.lookup(stop) + all_restriction:
                if a['adv'] == 'D' and stop_dep >= a['f'] and stop_dep <= a['t'] and ('tocs' not in a or op_next in a['tocs']): return False
                if a['adv'] == 'A' and stop_arr >= a['f'] and stop_arr <= a['t'] and ('tocs' not in a or op in a['tocs']): return False

    if 'trains' in restrictions[code] and restrictions[code]['info']['type_out'] == 'N':
        trains = restrictions[code]['trains']
        trains = ( train['id'] for train in trains if train['dir'] == 'O' )
        trains = ( train for train in trains if train in data['trains'] )
        for train in trains:
            journey = data['trains'][train]['stops']
            if fro in journey and to in journey and journey[fro][1] == dep and journey[to][0] == arr:
                return False

    return True
