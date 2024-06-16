from __future__ import division

import requests
import requests_cache
requests_cache.install_cache('split', expires_after=3600)

def fetch(url):
    r = requests.get(url, headers={
        'user-agent': 'split.traintimes.org.uk',
    })
    try:
        return r.json()
    except:
        return r.text

def price(n):
    if n == '-': return '-'
    return (u'\xa3%.2f' % (n/100)).replace('.00', '')

ticket_types = (
    'SOS', 'SOR', # Anytime single/return
    'SHR', # Anytime short return
    'SDS', 'SDR', # Anytime day
    'GTS', 'GTR', # Anytime single/return
    'GPR', # Anytime day return

    'CDS', 'CDR', # Off-peak day
    'SVS', 'SVR', 'SVH', # Off-peak
    'G2S', 'G2R', # Offpeak

    'SSS', 'SSR', 'OPS', 'OPR', # Super off-peak single/return
    'CBB', # Super off-peak single
    'SOP', # Super off-peak return
    # Super off-peak day
    'GDS', 'GDR', 'PDS', 'PDR',
    'SOA', 'SOB',
    'AM1', 'AM2',
    'EGS', 'EGF',
    'OPD',
    'SRR', 'SWS', 'SCO', 'C1R', 'CBA',

    # Travelcards
    #'ADT', # Anytime day
    #'AM3', 'OLT', 'SOT', 'STO', 'STP', 'WDT', 'WTC', # Super off-peak
    #'ODT', # Off-peak day

)
