# Load data

import json
import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

data_files = [ 'restrictions', 'stations', 'routes', 'routes.extra', 'clusters', 'tocs', 'trains' ]
data = {}
for d in data_files:
    with open(os.path.join(THIS_DIR, '..', 'data', d + '.json')) as fp:
        data[d] = json.load(fp)
