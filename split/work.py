import itertools

from split import fares, times
from split.data import data

def do_split(fr, to, day, time, via, exclude='', all_opts=''):
    context = {
        'from': fr,
        'to': to,
        'day': day,
        'time': time,
        'via': via,
    }
    store = context.copy()
    store.update( data={}, station_times={} )
    context.update(
        fr_desc = data['stations'][fr]['description'],
        to_desc = data['stations'][to]['description'],
    )

    store['station_times'][store['from']] = [ None, store['time'] ]
    all_stops_with_changes = times.find_stopping_points(store)
    if not all_stops_with_changes:
        context.update( error = True )
        return context
    store['all_stops'] = all_stops_with_changes
    context['all_stops_with_depart'] = [ (s, chg, data['stations'].get(s, { 'description': s }), store['station_times'][s]) for s,chg,op in all_stops_with_changes ]
    all_stops = [ s for s,_,_ in all_stops_with_changes ]

    context['exclude'] = filter(None, exclude.split(','))
    for ex in [ e for e in context['exclude'] if len(e) == 3 ]:
        while ex in all_stops: all_stops.remove(ex)

    stop_pairs = itertools.combinations(all_stops, 2)
    stop_pairs = filter(lambda x: x[0] != store['from'] or x[1] != store['to'], stop_pairs)
    Fares = fares.Fares(store)

    for ex in context['exclude']:
        if len(ex) == 2:
            Fares.excluded_restrictions.append(ex)
        else:
            Fares.excluded_routes.append(ex)

    context = split_journey(store, Fares, context, stop_pairs)
    context['all'] = all_opts
    if not all_opts:
        problem_routes = [ r for r in context['routes'] if r.get('problem') ]
        old_total = (0, 0)
        while problem_routes and old_total != (context['total'], context['fare_total']['fare']):
            context['skipped_problem_routes'] = True
            Fares.excluded_routes.append(problem_routes[0]['id'])
            old_total = (context['total'], context['fare_total']['fare'])
            context = split_journey(store, Fares, context, stop_pairs)
            problem_routes = [ r for r in context['routes'] if r.get('problem') ]

    return context

def split_journey(store, Fares, context, stop_pairs):
    routes = []
    restrictions = {}
    fare_total = Fares.parse_fare(store['from'], store['to'])
    context['fare_total'] = fare_total
    if fare_total['fare'] != '-':
        d = store['data'][store['from']][store['to']]
        if d['obj']['route']['desc'] != 'ANY PERMITTED':
            n = d['obj']['route']
            if n not in routes: routes.append(n)
        if d['obj']['restriction_code']:
            n = d['obj']['restriction_code']
            restrictions[n['id']] = n['desc']

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
        if d['obj']['route']['desc'] != 'ANY PERMITTED':
            n = d['obj']['route']
            if n not in routes: routes.append(n)
        if d['obj']['restriction_code']:
            n = d['obj']['restriction_code']
            restrictions[n['id']] = n['desc']

    context['output_cheapest'] = output_cheapest
    context['total'] = total
    context['routes'] = routes

    restrictions = dict( (k,v) for k,v in restrictions.items() if k not in ('8A', '4C') )
    context['restrictions'] = restrictions

    return context
