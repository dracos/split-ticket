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

def valid_journey(restrictions, fro, to, dep, arr, code):
    if not code.strip(): return True

    if dep: dep = dep[1].replace(':', '')
    if arr: arr = arr[0].replace(':', '')

    if 'trains' in restrictions[code] and restrictions[code]['info']['type_out'] == 'P':
        trains = restrictions[code]['trains']
        trains = ( train['id'] for train in trains if train['dir'] == 'O' )
        trains = ( train for train in trains if train in data['trains'] )
        trains = ( train for train in trains if train in data['trains'] )
        for train in trains:
            journey = data['trains'][train]['stops']
            if fro in journey and to in journey and journey[fro][1] == dep and journey[to][0] == arr:
                return True

    if 'times' in restrictions[code]:
        restriction = restrictions[code]['times']
        all_stations = restriction.get("")
        from_restriction = restriction.get(fro)
        to_restriction = restriction.get(to)
        #print code, fro, to, dep, arr, from_restriction, to_restriction, all_stations)

        if from_restriction:
            for i in from_restriction:
                if re.search('R$', i): continue
                a = from_restriction[i]
                if a['adv'] == 'D' and dep >= a['f'] and dep <= a['t']: return False
        if to_restriction:
            for i in to_restriction:
                if re.search('R$', i): continue
                a = to_restriction[i]
                if a['adv'] == 'A' and arr >= a['f'] and arr <= a['t']: return False
        if all_stations:
            for i in all_stations:
                if re.search('R$', i): continue
                a = all_stations[i]
                if a['adv'] == 'D' and dep >= a['f'] and dep <= a['t']: return False
                if a['adv'] == 'A' and arr >= a['f'] and arr <= a['t']: return False

    if 'trains' in restrictions[code] and restrictions[code]['info']['type_out'] == 'N':
        trains = restrictions[code]['trains']
        trains = ( train['id'] for train in trains if train['dir'] == 'O' )
        trains = ( train for train in trains if train in data['trains'] )
        trains = ( train for train in trains if train in data['trains'] )
        for train in trains:
            journey = data['trains'][train]['stops']
            if fro in journey and to in journey and journey[fro][1] == dep and journey[to][0] == arr:
                return False

    return True
