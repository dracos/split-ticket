#!/usr/bin/env python

import sys
from rq import Connection, Worker

import split.data

# Provide queue names to listen to as arguments to this script,
# similar to rqworker
with Connection():
    qs = sys.argv[1:] or ['default']
    w = Worker(qs)
    w.work()
