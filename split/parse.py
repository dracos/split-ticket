from datetime import date
import glob
import sys
from tqdm import tqdm

cnv_full_date = lambda x: date(int(x[4:8]), int(x[2:4]), int(x[0:2]))
cnv_str = lambda x: x.rstrip()

def unpack(row, *fields):
    ptr = 0
    data = {}
    for f in fields:
        fn = f[2] if len(f)==3 else cnv_str
        r = row[ptr:ptr+f[1]]
        data[f[0]] = fn(r)
        ptr += f[1]
    return data

def loop(f):
    started = False
    for row in progress(f):
        update_marker, row = row[0], row[1:].strip()

        if update_marker == '/':
            if not started: continue
            if 'End of file' in row: continue
        started = True
        assert update_marker == 'R'

        yield row

try:
    fares_dir = sys.argv[1]
    fares_files = glob.glob(fares_dir + '/*')
except IndexError:
    print >>sys.stderr, "Specify the fares directory as the first parameter"
    sys.exit(1)

def fare_file(ext):
    ext = '.%s' % ext
    match = list(filter(lambda x: ext in x, fares_files))
    assert len(match) == 1
    return match[0]


def progress(f):
    with open(f, "r") as fp:
        lines = sum(bl.count("\n") for bl in blocks(fp))
    return tqdm(open(f), total=lines)


def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b: break
        yield b
