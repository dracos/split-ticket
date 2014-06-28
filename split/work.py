import itertools

from split import fares, times
from split.data import data

def do_split(context):
    store = context.copy()

    context.update(
        fr_desc = data['stations'][context['from']]['description'],
        to_desc = data['stations'][context['to']]['description'],
    )

    stops = times.find_stopping_points(context)
    if not stops:
        context.update( error = True )
        return context
    context['stops'] = stops

    if context['time_ret']:
        stops_ret = times.find_stopping_points(context, ret=True)
        if not stops_ret:
            context.update( error = True )
            return context
        context['stops_ret'] = stops_ret
    else:
        stops_ret = None

    context['exclude'] = filter(None, context['exclude'].split(','))

    # Make a copy of the stops, to potentially exclude some
    stops_joint = [ s for s in stops if not context['time_ret'] or s in stops_ret ]
    excluded_stops = [ e for e in context['exclude'] if len(e) == 3 ]
    stops_joint = [ s for s in stops_joint if s.code not in excluded_stops ]
    context['stops_joint'] = stops_joint

    stop_pairs = itertools.combinations([ s.code for s in stops_joint ], 2)
    stop_pairs = filter(lambda x: x[0] != store['from'] or x[1] != store['to'], stop_pairs)
    Fares = fares.Fares(store, stops, stops_ret)

    for ex in context['exclude']:
        if len(ex) == 2:
            Fares.excluded_restrictions.append(ex)
        else:
            Fares.excluded_routes.append(ex)

    context = split_journey(store, Fares, context, stop_pairs)
    if not context['all']:
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
