from __future__ import division

import requests
import requests_cache
requests_cache.install_cache('split', expires_after=86400)

def fetch(url):
    r = requests.get(url)
    try:
        return r.json()
    except:
        return r.text

def price(n):
    if n == '-': return '-'
    return (u'\xa3%.2f' % (n/100)).replace('.00', '')
