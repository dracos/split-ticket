# vim: set fileencoding=utf-8 :

from __future__ import division

import json
import os
import re
from time import time as unix_time
import urllib.parse

import redis
R = redis.Redis()
from rq import Queue, Worker
from rq.job import Job

def get_job_id(context):
    id = '%(from)s/%(to)s/%(day)s/%(time)s/%(time_ret)s/%(via)s/%(exclude)s/%(all)s' % context
    if context.get('avoid'):
        id += '/%(avoid)s' % context
    return id

import bottle
from bottle import request

from split import utils

# Only need stations data here
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
data = {}
for d in [ 'stations' ]:
    with open(os.path.join(THIS_DIR, 'data', d + '.json')) as fp:
        data[d] = json.load(fp)
data['stations_by_name'] = dict( (v['description'], dict(list(v.items())+[('code',k)])) for k, v in data['stations'].items() )

def cache(s):
    """Decorator to set a cache-control header."""
    def decorator(func):
        def wrapper(*a, **ka):
            bottle.response.set_header('Cache-Control', 'max-age=%d' % s)
            return func(*a, **ka)
        return wrapper
    return decorator

def auth_basic(check):
    """Wrapper around bottle.auth_basic to strip any cache-control header."""
    orig = bottle.auth_basic(check)
    def decorator(func):
        def wrapper(*a, **ka):
            if 'Cache-Control' in bottle.response.headers:
                del bottle.response.headers['Cache-Control']
            return orig(func)(*a, **ka)
        return wrapper
    return decorator

@bottle.route('/robots.txt')
def robots():
    return bottle.static_file('robots.txt', root=os.path.join(THIS_DIR, 'static'))

@bottle.route('/static/<path:path>')
def server_static(path):
    return bottle.static_file(path, root=os.path.join(THIS_DIR, 'static'))

@bottle.route('/about')
@bottle.view('about')
@cache(60*15)
def about():
    pass

@bottle.route('/ajax-station')
@cache(60*15)
def ajax():
    q = request.query.query.lower()
    matches = list(filter(lambda x: x.lower().startswith(q), data['stations']))
    matches += list(filter(lambda x: x not in matches and data['stations'][x]['description'].lower().startswith(q), data['stations']))
    matches += list(filter(lambda x: x not in matches and q in data['stations'][x]['description'].lower(), data['stations']))
    return {
        'suggestions': [ data['stations'][m]['description'] for m in matches ]
    }

@bottle.route('/')
@cache(60*15)
def home():
    if all(x in request.query and request.query[x] for x in ['from', 'to', 'time', 'day']):
        request.query['time'] = re.sub('^(\d\d)(\d\d)$', r'\1:\2', request.query['time'])
        path = '/%(from)s/%(to)s/%(day)s/%(time)s' % request.query
        if request.query.get('time_ret'):
            request.query['time_ret'] = re.sub('^(\d\d)(\d\d)$', r'\1:\2', request.query['time_ret'])
            path += '/%(time_ret)s' % request.query
        if request.query.get('via'):
            path += '?via=' + urllib.parse.quote(request.query['via'])
        if request.query.get('avoid'):
            path += '?avoid=' + urllib.parse.quote(request.query['avoid'])
        bottle.redirect(path)
    return form(request.query)

def get_latest():
    latest = R.zrevrange('split-ticket-latest', 0, -1)
    if not latest: return []
    latest = list(filter(None, R.hmget('split-ticket-lines', latest)))
    return latest

@bottle.route('/ajax-latest')
def ajax_latest():
    return { 'latest': get_latest() }

@bottle.view('home')
def form(context):
    context['errors'] = clean(context)
    context['latest'] = get_latest()
    return context

def clean(form):
    errors = {}
    if not form: return errors
    if not form.get('from'):
        errors['from'] = 'Please enter an origin'
    elif form['from'] not in data['stations_by_name'] and form['from'] not in data['stations']:
        errors['from'] = 'Please select a valid origin'
    if not form.get('to'):
        errors['to'] = 'Please enter a destination'
    elif form['to'] not in data['stations_by_name'] and form['to'] not in data['stations']:
        errors['to'] = 'Please select a valid destination'
    if form.get('via') and form['via'] not in data['stations_by_name'] and form['via'] not in data['stations']:
        errors['via'] = 'Please select a valid via'
    if not form.get('day'):
        errors['day'] = 'Please say whether you want a single, day return, or return'
    if not form.get('time') or not re.match('\d\d:\d\d', form['time']):
        errors['time'] = 'Please enter a time'
    if form.get('time_ret') and not re.match('\d\d:\d\d', form['time_ret']):
        errors['time_ret'] = 'Please enter a valid time'
    return errors

def make_url(fr=None, to=None):
    path = request.path.split('/')
    if fr: path[1] = fr
    if to: path[2] = to
    path = '/'.join(path)
    qs = request.query_string
    if qs: qs = '?' + qs
    return path + qs

def context_init(fr, to, day, time, time_ret):
    ctx = {
        'from': fr,
        'to': to,
        'day': day,
        'time': time,
        'time_ret': time_ret,
        'via': request.query.via,
        'exclude': request.query.exclude,
        'all': request.query.all,
    }
    if request.query.avoid:
        ctx['avoid'] = request.query.avoid
    return ctx

@bottle.route('/ajax-job/<fr>/<to>/<day>/<time>')
def split_ajax_no_ret(fr, to, day, time):
    return split_ajax(fr, to, day, time, '')

@bottle.route('/ajax-job/<fr>/<to>/<day>/<time>/<time_ret>')
def split_ajax(fr, to, day, time, time_ret):
    bottle.response.set_header('Cache-Control', 'max-age=0')
    context = context_init(fr, to, day, time, time_ret)

    q = Queue(connection=R)
    job = q.fetch_job(get_job_id(context))

    done = job and (job.is_finished or job.is_failed)
    include_me = 1 if job else 0
    busy_workers = len([ w for w in Worker.all(connection=R) if w.get_state() == 'busy' ]) - include_me
    busy_workers += q.count
    return {
        'done': done,
        'refresh': max(1, busy_workers),
        'queue_size': max(0, busy_workers),
    }

@bottle.route('/<fr>/<to>/<day>/<time>')
def split(fr, to, day, time):
    return _split(fr, to, day, time, '')

@bottle.route('/<fr>/<to>/<day>/<time>/<time_ret>')
@bottle.view('please_wait')
def _split(fr, to, day, time, time_ret):
    context = context_init(fr, to, day, time, time_ret)

    if (fr.upper() in data['stations'] and fr not in data['stations']) or (to.upper() in data['stations'] and to not in data['stations']):
        bottle.redirect(make_url(fr=fr.upper(), to=to.upper()))

    context['errors'] = clean(context)
    if context['errors']:
        return form(context)

    if fr in data['stations_by_name'] or to in data['stations_by_name']:
        if fr in data['stations_by_name']: fr = data['stations_by_name'][fr]['code']
        if to in data['stations_by_name']: to = data['stations_by_name'][to]['code']
        bottle.redirect(make_url(fr=fr, to=to))

    q = Queue(connection=R)
    job_id = get_job_id(context)
    job = q.fetch_job(job_id)
    include_me = 0

    if job and (job.is_finished or job.is_failed):
        if not job.result or 'error' in job.result: return error(job.result)
        return split_finished(job.result)

    if job:
        include_me = 1
    else:
        ua = request.headers.get('User-Agent', '')
        if 'bot' not in ua and 'spider' not in ua:
            job = q.enqueue('split.work.do_split', context, job_id=job_id)

    bottle.response.set_header('Cache-Control', 'max-age=0')

    busy_workers = len([ w for w in Worker.all(connection=R) if w.get_state() == 'busy' ]) - include_me
    busy_workers += q.count
    context.update({
        'fr_desc': data['stations'][fr]['description'],
        'to_desc': data['stations'][to]['description'],
        'url_job': make_url(),
        'refresh': max(1, busy_workers),
        'queue_size': max(0, busy_workers),
    })
    return context

@bottle.view('result')
def split_finished(context):
    bottle.response.set_header('Cache-Control', 'max-age=900')
    fare_total = context['fare_total']
    total = context['total']
    if fare_total['fare'] != '-' and total < fare_total['fare'] and not context['exclude'] and not request.query.all:
        typ = ''
        if context['day'] == 'y':
            typ = ' for the day'
        elif context['day'] == 'n':
            typ = ' return'
        line = u'%s to %s%s, around %s – <a href="%s">%s</a> instead of %s (<strong>%d%%</strong> saving)' % (
            context['fr_desc'], context['to_desc'],
            typ, context['time'],
            make_url(), utils.price(total),
            utils.price(fare_total['fare']), 100-round(total/fare_total['fare']*100)
        )
        key = '%s%s' % (context['from'], context['to'])
        pipe = R.pipeline()
        pipe.hset( 'split-ticket-lines', key, line )
        pipe.zadd( 'split-ticket-latest', {key: unix_time()} )
        pipe.zremrangebyrank( 'split-ticket-latest', 0, -11 )
        pipe.incrby( 'split-ticket-total-saved', int(fare_total['fare'] - total) )
        pipe.incrby( 'split-ticket-total-orig', int(fare_total['fare']) )
        pipe.incrby( 'split-ticket-total-split', int(total) )
        pipe.execute()

    return context

@bottle.view('error')
def error(context):
    bottle.response.status = 500
    return context

if __name__ == "__main__":
    bottle.run(host='localhost', port=8080, debug=True, reloader=True)

os.chdir(os.path.dirname(__file__))
application = bottle.default_app()
