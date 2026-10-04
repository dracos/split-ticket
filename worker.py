#!/usr/bin/env python

import sys
from rq import Worker

import split.data

import redis
R = redis.Redis()

# Provide queue names to listen to as arguments to this script,
# similar to rqworker
qs = sys.argv[1:] or ['default']
w = Worker(qs, connection=R)
w.work()
