import re

from . import utils, restrictions

TICKET_NAMES = {
    'SOR': 'Anytime Return',
    'SVR': 'Off-peak Return',
    'SDR': 'Anytime Day Return',
    'CDR': 'Off-peak Day Return',
    'SOS': 'Anytime Single',
    'SDS': 'Anytime Day Single',
    'CDS': 'Cheap Day Single',
}

class Fares(object):
    excluded_routes = []

    def __init__(self, store, data):
        self.store = store
        self.data = data

    def prettify(self, s):
        s = re.sub('\w\S*', lambda txt: txt.group().title(), s)
        s = re.sub(' R$', ' Return', s)
        s = re.sub(' S$', ' Single', s)
        return s

    def get_fares_old(self):
        data = utils.fetch('http://api.brfares.com/querysimple?orig=' + self.fro + '&dest=' + self.to)
        return data['fares']

    def get_codes(self, stn):
        stn = self.data['stations'][stn]
        stn_codes = stn['codes'] + sum([ self.data['clusters'][x] for x in stn['codes'] ], [])
        return stn['description'], stn_codes

    def get_fares(self):
        name_fr, codes_fr = self.get_codes(self.fro)
        name_to, codes_to = self.get_codes(self.to)

        froms = filter(None, map(lambda x: self.data['fares'].get(x), codes_fr))
        fares = []
        for f in froms:
            matches = filter(None, map(lambda x: f.get(x), codes_to))
            fares.extend( [ p for m in matches for p in m ] )
        froms = filter(None, map(lambda x: self.data['fares'].get(x), codes_to))
        for f in froms:
            matches = filter(None, map(lambda x: f.get(x), codes_fr))
            fares.extend( [ p for m in matches for p in m if p['direction'] == 'R' ] )

        data = []
        for f in fares:
            for t, p in f['prices'].items():
                data.append({
                    'toc': f['toc'], 'route': { 'name': self.data['routes'][f['route']] },
                    'ticket': { 'code': t, 'name': TICKET_NAMES[t] }, 'adult': { 'fare': int(p[0]) }, 'restriction_code': p[1],
                })
        return data

    def fare_desc(self, s):
        o = s['ticket']['name']
        if s['route']['name'] != 'ANY PERMITTED': o += ', ' + self.prettify(s['route']['name'])
        # if s['restriction_code'] != '  ': o += ', ' + s['restriction_code']
        if self.double: o += ' (2 singles)'
        return o

    def is_valid_journey(self, s):
        return restrictions.valid_journey(
            self.data['restrictions'],
            self.fro, self.to,
            self.store['station_times'].get(self.fro), self.store['station_times'].get(self.to),
            s['restriction_code']
        )

    def is_valid_route(self, s):
        return s['route']['name'] not in self.excluded_routes

    def match_returns(self, s):
        ret = re.search('SVR|SOR', s['ticket']['code'])
        if self.store['day']:
            ret = ret or re.search('CDR|SDR', s['ticket']['code'])
        ret = ret and self.is_valid_journey(s)
        ret = ret and self.is_valid_route(s)
        return ret

    def match_singles(self, s):
        ret = re.search('CDS|SDS|SOS', s['ticket']['code'])
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
        if best:
            pass
        else:
            singles = filter(self.match_singles, price_data)
            for r in singles:
                if not best or r['adult']['fare'] < best['adult']['fare']:
                    best = r
            if best:
                self.double = True

        if not best:
            return { 'fare': '-', 'obj': None, 'desc': '-' }

        fare = best['adult']['fare'] * (2 if self.double else 1)
        if fro not in self.store['data']: self.store['data'][fro] = {}
        if to not in self.store['data']: self.store['data'][to] = {}
        self.store['data'][fro][to] = { 'fare': fare, 'obj': best, 'desc': self.fare_desc(best) }
        return self.store['data'][fro][to]
