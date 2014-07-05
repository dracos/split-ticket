# vim: set fileencoding=utf-8 :

import json
import re

from . import restrictions, dijkstra
from .utils import price
from .data import data

TICKET_BY_TYPE = {
    'Anytime Return': [ 'SOR', 'GTR' ],
    'Anytime Day Return': [ 'SDR', 'GPR' ],
    'Anytime Single': [ 'SOS', 'GTS' ],
    'Anytime Day Single': [ 'SDS' ],

    'Off-peak Return': [ 'SVR', 'G2R' ],
    'Off-peak Day Return': [ 'CDR' ],
    'Off-peak Single': [ 'SVS', 'SVH', 'G2S', 'CDS' ],

    'Super off-peak Return': [ 'SSR', 'OPR', 'SOP' ],
    'Super off-peak Single': [ 'SSS', 'OPS', 'CBB' ],
    'Super off-peak Day Return': [ 'GDR', 'PDR', 'SOB', 'AM2', 'EGF', 'SRR', 'SWS', 'SCO', 'C1R', 'CBA' ],
    'Super off-peak Day Single': [ 'GDS', 'PDS', 'SOA', 'AM1', 'EGS', 'OPD' ],
}
TICKET_NAMES = {}
for name, types in TICKET_BY_TYPE.items():
    for t in types:
        TICKET_NAMES[t] = name

FARES = {}

class Fares(object):
    def __init__(self, store, stops, stops_ret):
        self.store = store
        self.stops = stops
        self.stops_ret = stops_ret
        self.excluded_routes = []
        self.excluded_restrictions = []
        self.restrictions = restrictions.Restriction(stops, stops_ret)

    def prettify(self, s):
        s = re.sub('\w\S*', lambda txt: txt.group().title(), s)
        return s

    def get_codes(self, stn):
        # Return in this order so that override will function
        if stn not in data['stations']: return []
        stn = data['stations'][stn]
        stn_codes = []
        stn_codes += data['clusters'].get(stn.get('fare_group'), [])
        stn_codes += data['clusters'].get(stn['code'], [])
        stn_codes += [ stn['fare_group'] ] if 'fare_group' in stn else []
        stn_codes += [ stn['code'] ]
        return stn_codes

    def get_fare_entry(self, code):
        if code not in FARES:
            try:
                with open('data/fares/%s.json' % code) as fp:
                    FARES[code] = json.load(fp)
            except IOError:
                FARES[code] = None
        return FARES[code]

    def get_fares(self, fro, to):
        codes_fr = self.get_codes(fro)
        codes_to = self.get_codes(to)

        froms = filter(None, map(lambda x: self.get_fare_entry(x), codes_fr))
        # Fares by ROUTE because for the same route, individual flow overrides
        # fare_group which overrides cluster
        fares = {}
        for f in froms:
            matches = filter(None, map(lambda x: f.get(x), codes_to))
            for m in matches:
                for p in m:
                    fares[p['route']] = p

        fares_data = []
        for f in fares.values():
            for t, p in f['prices'].items():
                restriction = None
                if p[1]:
                    desc_out = data['restrictions'][p[1]]['info']['desc_out'].title()
                    desc_rtn = data['restrictions'][p[1]]['info']['desc_rtn'].title()
                    if desc_out == desc_rtn:
                        desc = desc_out
                    else:
                        desc = 'Out: %s, Return: %s' % (desc_out, desc_rtn)
                    restriction = { 'id': p[1], 'desc': desc, 'desc_out': desc_out, 'desc_rtn': desc_rtn }
                route = data['routes'][f['route']]
                route['id'] = f['route']
                fares_data.append({
                    'toc': f.get('toc'),
                    'route': route,
                    'ticket': { 'code': t, 'name': TICKET_NAMES[t] },
                    'adult': { 'fare': int(p[0]) },
                    'restriction_code': restriction,
                })
        return fares_data

    def fare_desc(self, fares):
        if len(fares)>1:
            out = '<ul>'
            out += '<li>Out: ' + self._fare_desc(fares[0], 2, 'O')
            out += '<li>Return: ' + self._fare_desc(fares[1], 2, 'R')
            out += '</ul>'
            return out
        else:
            return self._fare_desc(fares[0], 1, 'O')

    def _fare_desc(self, s, n, dir):
        dir_split = 'B'
        if n>1: dir_split = dir
        o = s['ticket']['name']
        if s['route']['desc'] != 'ANY PERMITTED':
            ops = self.operators(dir)
            rte = self.prettify(s['route']['desc'])
            extra = data['routes'][s['route']['id']].get('operator')
            if extra and ops != set(extra):
                ops = map(lambda x: data['tocs'].get(x, x), ops)
                rte = '<strong>' + rte + '</strong> (train is %s)' % '/'.join(ops)
                s['route']['problem'] = dir_split
            ibs = set([ i.code for i in self.inbetween_stops(dir) ])
            if dir == 'R' and self.stops_ret:
                ibs = ibs | set((self.to,))
            else:
                ibs = ibs | set((self.fro,))
            if ('E' in s['route'] and set(s['route']['E']) & ibs) or \
               ('I' in s['route'] and not set(s['route']['I']) & ibs):
                rte = '<strong>' + rte + '</strong> (station requirement may not be met<sup><a href="/about#passing-through">*</a></sup>)'
                s['route']['problem'] = dir_split
            o += ', ' + rte
        if s['restriction_code']:
            desc = 'desc_out' if n>1 else 'desc'
            o += ', ' + s['restriction_code'][desc]
            o += ' (code %s)' % s['restriction_code']['id']
        if 'Single' in o and n>1:
            o += u', ' + price(s['adult']['fare'])
        return o

    def is_valid_journey(self, s, dir):
        restriction_code = s['restriction_code']['id'] if s['restriction_code'] else ''
        if restriction_code in self.excluded_restrictions:
            return False
        return self.restrictions.valid_journey(self.fro, self.to, restriction_code, dir)

    def is_valid_route(self, s, dir):
        if not self.split_singles:
            routes = [ re.sub('[or]$', '', r) for r in self.excluded_routes ]
        elif dir == 'R':
            routes = [ re.sub('r$', '', r) for r in self.excluded_routes ]
        elif dir == 'O':
            routes = [ re.sub('o$', '', r) for r in self.excluded_routes ]
        else:
            routes = self.excluded_routes
        return s['route']['id'] not in routes

    def match_returns(self, s):
        ret = re.search('SOR|GTR|SVR|G2R|SSR|OPR|SOP', s['ticket']['code'])
        if self.store['day'] == 'y':
            ret = ret or re.search('SDR|GPR|CDR|GDR|PDR|SOB|AM2|EGF|SCO|C1R|CBA|SRR|SWS', s['ticket']['code'])
        ret = ret and self.is_valid_journey(s, 'B')
        ret = ret and self.is_valid_route(s, 'B')
        return ret

    def match_singles_out(self, s):
        return self._match_singles(s, 'O')

    def match_singles_ret(self, s):
        return self._match_singles(s, 'R')

    def _match_singles(self, s, dir):
        ret = re.search('SOS|SDS|GTS|CDS|SVS|G2S|SSS|OPS|CBB|GDS|PDS|SOA|AM1|EGS|OPD', s['ticket']['code'])
        ret = ret and self.is_valid_journey(s, dir)
        ret = ret and self.is_valid_route(s, dir)
        return ret

    def parse_fare(self, fro, to, split_singles=True):
        self.fro = fro
        self.to = to
        self.split_singles = split_singles
        price_data_ret = price_data = self.get_fares(fro, to)
        if self.stops_ret and split_singles:
            price_data_ret = self.get_fares(to, fro)

        best = ()
        singles = filter(self.match_singles_out, price_data)
        if self.store['day'] == 's':
            for r in singles:
                if not best or r['adult']['fare'] < best[0]['adult']['fare']:
                    best = (r,)
        else:
            returns = filter(self.match_returns, price_data)
            for r in returns:
                if not best or r['adult']['fare'] < best[0]['adult']['fare']:
                    best = (r,)

            match = self.match_singles_ret if split_singles else self.match_singles_out
            singles_ret = filter(match, price_data_ret)
            for i in singles:
                for j in singles_ret:
                    curr_best_fare = sum( f['adult']['fare'] for f in best )
                    if not best or i['adult']['fare']+j['adult']['fare'] < curr_best_fare:
                        best = (i,j)

        if not best:
            return { 'fare': '-', 'obj': None, 'desc': '-' }

        fare = sum( f['adult']['fare'] for f in best )
        if fro not in self.store['data']: self.store['data'][fro] = {}
        if to not in self.store['data']: self.store['data'][to] = {}
        self.store['data'][fro][to] = { 'fare': fare, 'obj': best, 'desc': self.fare_desc(best) }
        return self.store['data'][fro][to]

    def find_cheapest(self):
        graph = dijkstra.Graph()
        for x in self.store['data'].keys():
            graph.add_node(x)

        for x in self.store['data'].keys():
            for y in self.store['data'][x].keys():
                if self.store['data'][x][y]['fare'] != -1:
                    graph.add_edge(x, y, self.store['data'][x][y]['fare'])

        result, path = dijkstra.dijkstra(graph, self.store['from'])
        node = self.store['to']
        nodes = [];
        while node:
            nodes.append(node)
            node = path.get(node)

        nodes.reverse()
        total = 0
        out = []
        for i in range(0, len(nodes)-1):
            f = nodes[i]
            t = nodes[i+1]
            d = self.store['data'][f][t]
            out.append( (f,t,d) )
            total += d['fare']
        return out, total

    def inbetween_stops(self, dir):
        if dir == 'R' and self.stops_ret:
            dir_stops = self.stops_ret
            fro = self.to
            to = self.fro
        else:
            dir_stops = self.stops
            fro = self.fro
            to = self.to
        stops = []
        started = False
        for stop in dir_stops:
            if stop.code == fro:
                started = True
                continue
            if started:
                stops.append(stop)
            if stop.code == to:
                started = False
        return stops

    def operators(self, dir):
        stops = self.inbetween_stops(dir)
        stops = ( s.operator for s in stops if s.operator is not None )
        return set(stops)
