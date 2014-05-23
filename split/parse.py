from datetime import date

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
    for row in open(f):
        update_marker, row = row[0], row[1:].strip()

        if update_marker == '/':
            if not started: continue
            if 'End of file' in row: continue
        started = True
        assert update_marker == 'R'

        yield row
