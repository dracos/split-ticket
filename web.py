# vim: set fileencoding=utf-8 :

from __future__ import division

import json
import os
import re
from time import time as unix_time
import urllib

import redis
R = redis.Redis()
from rq import Queue, Worker
from rq.job import Job

class MyJob(Job):
    @classmethod
    def create(cls, *args, **kwargs):
        job = super(MyJob, cls).create(*args, **kwargs)
        # Yuck
        args = [ a for a in args[1] ]
        args[2] = 'y' if args[2] else 'n'
        job.id = '/'.join(args)
        return job

class MyQueue(Queue):
    job_class = MyJob

import bottle
from bottle import request

from split import utils

# Only need stations data here
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
data = {}
for d in [ 'stations' ]:
    with open(os.path.join(THIS_DIR, 'data', d + '.json')) as fp:
        data[d] = json.load(fp)
data['stations_by_name'] = dict( (v['description'], dict(v.items()+[('code',k)])) for k, v in data['stations'].items() )

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

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

@bottle.route('/robots.txt')
@cache(60*15)
def robots():
    return bottle.static_file('robots.txt', root=os.path.join(THIS_DIR, 'static'))

@bottle.route('/static/<path:path>')
@cache(60*15)
def server_static(path):
    return bottle.static_file(path, root=os.path.join(THIS_DIR, 'static'))

@bottle.route('/bower/<path:path>')
@cache(60*15)
def server_static(path):
    return bottle.static_file(path, root=os.path.join(THIS_DIR, 'bower_components'))

@bottle.route('/about')
@bottle.view('about')
@cache(60*15)
def about():
    pass

@bottle.route('/ajax-station')
@cache(60*15)
def ajax():
    q = request.query.query.lower()
    matches = filter(lambda x: x.lower().startswith(q), data['stations'])
    matches += filter(lambda x: x not in matches and data['stations'][x]['description'].lower().startswith(q), data['stations'])
    matches += filter(lambda x: x not in matches and q in data['stations'][x]['description'].lower(), data['stations'])
    return {
        'suggestions': [ data['stations'][m]['description'] for m in matches ]
    }

@bottle.route('/')
@cache(60*15)
def home():
    if all(x in request.query and request.query[x] for x in ['from', 'to', 'time', 'day']):
        path = '/%(from)s/%(to)s/%(day)s/%(time)s' % request.query
        if request.query.get('via'):
            path += '?via=' + urllib.quote(request.query['via'])
        bottle.redirect(path)
    return form(request.query)

@bottle.route('/ajax-latest')
def ajax_latest():
    return {
        'latest': R.zrevrange('split-ticket-latest', 0, -1)
    }

@bottle.view('home')
def form(context):
    context['errors'] = clean(context)
    context['latest'] = R.zrevrange('split-ticket-latest', 0, -1)
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
        errors['day'] = 'Please say whether you are travelling for the day'
    if not form.get('time') or not re.match('\d\d:\d\d', form['time']):
        errors['time'] = 'Please enter a time'
    return errors

@bottle.route('/<fr>/<to>/<day>/<time>')
@bottle.view('please_wait')
def split(fr, to, day, time):
    via = request.query.get('via', '')

    if (fr.upper() in data['stations'] and fr not in data['stations']) or (to.upper() in data['stations'] and to not in data['stations']):
        qs = request.query_string
        if qs: qs = '?' + qs
        bottle.redirect('/%s/%s/%s/%s%s' % (fr.upper(), to.upper(), day, time, qs))

    errors = clean({ 'from': fr, 'to': to, 'day': day, 'time': time, 'via': via })
    if errors:
        return form({ 'from': fr, 'to': to, 'day': day, 'time': time, 'via': via, 'errors': errors })

    if fr in data['stations_by_name'] or to in data['stations_by_name']:
        if fr in data['stations_by_name']: fr = data['stations_by_name'][fr]['code']
        if to in data['stations_by_name']: to = data['stations_by_name'][to]['code']
        qs = request.query_string
        if qs: qs = '?' + qs
        bottle.redirect('/%s/%s/%s/%s%s' % (fr, to, day, time, qs))

    job_id = '/'.join((fr, to, day, time, via, request.query.exclude, request.query.all))
    day = day == 'y'

    q = MyQueue(connection=R)
    job = q.fetch_job(job_id)
    include_me = 0

    if job and (job.is_finished or job.is_failed):
        if 'error' in job.result: return error(job.result)
        return split_finished(job.result)
    if job:
        include_me = 1
    else:
        job = q.enqueue('split.work.do_split', fr, to, day, time, via, request.query.exclude, request.query.all)

    busy_workers = len([ w for w in Worker.all(connection=R) if w.get_state() == 'busy' ]) - include_me
    busy_workers += q.count
    qs = request.query_string
    if qs: qs = '?' + qs
    url_job = '%s%s' % (request.path, qs)
    context = {
        'from': fr,
        'to': to,
        'day': day,
        'time': time,
        'via': via,
        'fr_desc': data['stations'][fr]['description'],
        'to_desc': data['stations'][to]['description'],
        'url_job': url_job,
        'refresh': max(2, busy_workers),
        'queue_size': max(0, busy_workers),
    }
    return context

@bottle.view('result')
def split_finished(context):
    bottle.response.set_header('Cache-Control', 'max-age=900')
    fare_total = context['fare_total']
    total = context['total']
    if fare_total['fare'] != '-' and total < fare_total['fare'] and not context['exclude']:
        qs = request.query_string
        if qs: qs = '?' + qs
        line = u'%s to %s%s, around %s – <a href="%s%s">%s</a> instead of %s (<strong>%d%%</strong> saving)' % (
	    context['fr_desc'], context['to_desc'],
            ' for the day' if context['day'] else '', context['time'],
            request.path, qs, utils.price(total),
            utils.price(fare_total['fare']), 100-round(total/fare_total['fare']*100)
        )
        pipe = R.pipeline()
        pipe.zadd( 'split-ticket-latest', line, unix_time() )
        pipe.zremrangebyrank( 'split-ticket-latest', 0, -6 )
        pipe.execute()

    return context

@bottle.view('error')
def error(context):
    return context

if __name__ == "__main__":
    bottle.run(host='localhost', port=8080, debug=True, reloader=True)
app = bottle.default_app()
