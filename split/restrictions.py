import json
import os
import re

def valid_journey(restrictions, fro, to, dep, arr, code):
    if not code.strip(): return True
    if 'times' not in restrictions[code]: return True
    restriction = restrictions[code]['times']
    all_stations = restriction.get("")
    from_restriction = restriction.get(fro)
    to_restriction = restriction.get(to)
    if dep: dep = dep[1].replace(':', '')
    if arr: arr = arr[0].replace(':', '')
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

    return True
