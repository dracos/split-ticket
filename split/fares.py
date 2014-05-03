import re

from . import utils, restrictions

def prettify(s):
    s = re.sub('\w\S*', lambda txt: txt.group().title(), s)
    s = re.sub(' R$', ' Return', s)
    s = re.sub(' S$', ' Single', s)
    return s

def parse_fare(store, fro, to):
    body = utils.fetch('http://api.brfares.com/querysimple?orig=' + fro + '&dest=' + to)

    def fare_list(s):
        o = utils.price(s['adult']['fare'])
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
    disp = utils.price(fare)
    if double: disp += ' (2 singles)'
    return disp
