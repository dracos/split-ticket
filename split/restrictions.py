import re

from split.data import data

class SingleRestriction(object):
    def __init__(self, restriction):
        self.restriction = restriction

    def lookup(self, s):
        resp = self.restriction.get(s, {})
        resp = [ v for k,v in resp.items() if not re.search('R$', k) ]
        return resp

class Restriction(object):
    def __init__(self, stops, stops_ret):
        self.stops = { 'O': stops, 'R': stops_ret }

    def get_time(self, stop, dir):
        t = stop.times[dir]
        if t: t = t.replace(':', '')
        return t

    def considered_stops(self, fro, to, dir):
        """Origin, destination, and anywhere we change"""
        stops = []
        started = False
        for stop in self.stops[dir]:
            chg = stop.change
            if stop.code == fro or stop.code == to:
                started = chg = True
            if started and chg:
                stops.append(stop)
            if stop.code == to:
                break
        return stops

    def next_stop(self, stop, dir):
        found = False
        for s in self.stops[dir]:
            if found == True:
                return s
            if s == stop:
                found = True

    def valid_journey(self, fro, to, code, dir):
        if not code.strip(): return True
        valid = True
        if dir in ('O', 'B') or not self.stops['R']:
            valid &= self._valid_journey(fro, to, code, 'O')
        if dir in ('R', 'B') and self.stops['R']:
            valid &= self._valid_journey(to, fro, code, 'R')
        return valid

    def _valid_journey(self, fro, to, code, ret):
        dep = self.get_time(self.stops[ret][fro], 1)
        arr = self.get_time(self.stops[ret][to], 0)

        restrictions = data['restrictions']
        if 'trains' in restrictions[code] and restrictions[code]['info']['type_out'] == 'P':
            trains = restrictions[code]['trains']
            trains = ( train['id'] for train in trains if train['dir'] == ret )
            trains = ( train for train in trains if train in data['trains'] )
            for train in trains:
                if train not in data['trains']: continue
                if 'stops' not in data['trains'][train]: continue
                journey = data['trains'][train]['stops']
                if fro in journey and to in journey and journey[fro][1] == dep and journey[to][0] == arr:
                    return True

        if 'times' in restrictions[code]:
            restriction = SingleRestriction(restrictions[code]['times'])
            all_restriction = restriction.lookup("")
            for stop in self.considered_stops(fro, to, ret):
                stop_next = self.next_stop(stop, ret)
                stop_arr = self.get_time(stop, 0)
                stop_dep = self.get_time(stop, 1)
                for a in restriction.lookup(stop.code) + all_restriction:
                    if a['adv'] == 'D' and stop_dep >= a['f'] and stop_dep <= a['t'] and ('tocs' not in a or stop_next.operator in a['tocs']): return False
                    if a['adv'] == 'A' and stop_arr >= a['f'] and stop_arr <= a['t'] and ('tocs' not in a or stop.operator in a['tocs']): return False

        if 'trains' in restrictions[code] and restrictions[code]['info']['type_out'] == 'N':
            trains = restrictions[code]['trains']
            trains = ( train['id'] for train in trains if train['dir'] == ret )
            trains = ( train for train in trains if train in data['trains'] )
            for train in trains:
                if train not in data['trains']: continue
                if 'stops' not in data['trains'][train]: continue
                journey = data['trains'][train]['stops']
                if fro in journey and to in journey and journey[fro][1] == dep and journey[to][0] == arr:
                    return False

        return True
