# vim: set fileencoding=utf-8 :

import json
import re

from . import restrictions, dijkstra
from .utils import price

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

class Fares(object):
    def __init__(self, store, data):
        self.store = store
        self.data = data
        self.excluded_routes = []
        self.excluded_restrictions = []
        self.fares = {}

    def prettify(self, s):
        s = re.sub('\w\S*', lambda txt: txt.group().title(), s)
        return s

    def get_codes(self, stn):
        # Return in this order so that override will function
        if stn not in self.data['stations']: return []
        stn = self.data['stations'][stn]
        stn_codes = []
        stn_codes += self.data['clusters'].get(stn.get('fare_group'), [])
        stn_codes += self.data['clusters'].get(stn['code'], [])
        stn_codes += [ stn['fare_group'] ] if 'fare_group' in stn else []
        stn_codes += [ stn['code'] ]
        return stn_codes

    def get_fare_entry(self, code):
        if code not in self.fares:
            try:
                with open('data/fares/%s.json' % code) as fp:
                    self.fares[code] = json.load(fp)
            except IOError:
                self.fares[code] = None
        return self.fares[code]

    def get_fares(self):
        codes_fr = self.get_codes(self.fro)
        codes_to = self.get_codes(self.to)

        froms = filter(None, map(lambda x: self.get_fare_entry(x), codes_fr))
        # Fares by ROUTE because for the same route, individual flow overrides
        # fare_group which overrides cluster
        fares = {}
        for f in froms:
            matches = filter(None, map(lambda x: f.get(x), codes_to))
            for m in matches:
                for p in m:
                    fares[p['route']] = p

        data = []
        for f in fares.values():
            for t, p in f['prices'].items():
                restriction = None
                if p[1]:
                    desc_out = self.data['restrictions'][p[1]]['info']['desc_out'].title()
                    desc_rtn = self.data['restrictions'][p[1]]['info']['desc_rtn'].title()
                    if desc_out == desc_rtn:
                        desc = desc_out
                    else:
                        desc = 'Out: %s, Return: %s' % (desc_out, desc_rtn)
                    restriction = { 'id': p[1], 'desc': desc }
                route = self.data['routes'][f['route']]
                route['id'] = f['route']
                data.append({
                    'toc': f.get('toc'),
                    'route': route,
                    'ticket': { 'code': t, 'name': TICKET_NAMES[t] },
                    'adult': { 'fare': int(p[0]) },
                    'restriction_code': restriction,
                })
        return data

    def fare_desc(self, s):
        o = s['ticket']['name']
        if s['route']['desc'] != 'ANY PERMITTED':
            ops = self.operators()
            rte = self.prettify(s['route']['desc'])
            if self.data['routes.extra'].get(s['route']['id']):
                extra = self.data['routes.extra'][s['route']['id']]
                if len(ops) > 1 or (len(ops) ==1 and extra.get('operator') and extra['operator'] != list(ops)[0]):
                    ops = map(lambda x: self.data['tocs'].get(x, x), ops)
                    rte = '<strong>' + rte + '</strong> (train is %s)' % '/'.join(ops)
            ibs = set([ i[0] for i in self.inbetween_stops() ]) | set(self.fro)
            if ('E' in s['route'] and set(s['route']['E']) & ibs) or \
               ('I' in s['route'] and not set(s['route']['I']) & ibs):
                rte = '<strong>' + rte + '</strong> (station requirement not met)'
            o += ', ' + rte
        if s['restriction_code']:
            o += ', ' + s['restriction_code']['desc']
            o += ' (%s)' % s['restriction_code']['id']
        if self.double:
            o += u', 2 × ' + price(s['adult']['fare'])
        return o

    def is_valid_journey(self, s):
        restriction_code = s['restriction_code']['id'] if s['restriction_code'] else ''
        if restriction_code in self.excluded_restrictions:
            return False
        return restrictions.valid_journey(
            self.data['restrictions'],
            self.fro, self.to,
            self.store['all_stops'],
            self.store['station_times'],
            restriction_code
        )

    def is_valid_route(self, s):
        return s['route']['id'] not in self.excluded_routes

    def match_returns(self, s):
        ret = re.search('SOR|GTR|SVR|G2R|SSR|OPR|SOP', s['ticket']['code'])
        if self.store['day']:
            ret = ret or re.search('SDR|GPR|CDR|GDR|PDR|SOB|AM2|EGF|SCO|C1R|CBA|SRR|SWS', s['ticket']['code'])
        ret = ret and self.is_valid_journey(s)
        ret = ret and self.is_valid_route(s)
        return ret

    def match_singles(self, s):
        ret = re.search('SOS|SDS|GTS|CDS|SVS|SVH|G2S|SSS|OPS|CBB|GDS|PDS|SOA|AM1|EGS|OPD', s['ticket']['code'])
        ret = ret and self.is_valid_journey(s)
        ret = ret and self.is_valid_route(s)
        return ret

    def parse_fare(self, fro, to):
        self.fro = fro
        self.to = to
        price_data = self.get_fares()

        returns = filter(self.match_returns, price_data)

        best = None
        for r in returns:
            if not best or r['adult']['fare'] < best['adult']['fare']:
                best = r

        self.double = False
        singles = filter(self.match_singles, price_data)
        for r in singles:
            if not best or r['adult']['fare']*2 < best['adult']['fare']*(2 if self.double else 1):
                best = r
                self.double = True

        if not best:
            return { 'fare': '-', 'obj': None, 'desc': '-' }

        fare = best['adult']['fare'] * (2 if self.double else 1)
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

    def inbetween_stops(self):
        stops = []
        started = False
        for stop, chg, op in self.store['all_stops']:
            if stop == self.fro:
                started = True
                continue
            if started:
                stops.append((stop, chg, op))
            if stop == self.to:
                started = False
        return stops

    def operators(self):
        stops = self.inbetween_stops()
        stops = ( s[2] for s in stops if s[2] is not None )
        return set(stops)
