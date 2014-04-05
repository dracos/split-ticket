exports.combination = function(pool, r) {
    var n = pool.length,
        indices = range(r),
        out = [];

    if (r > n)
        return;

    out.push( range(r).map(function(x){ return pool[indices[x]] }) )
    while (1) {
        for (i=r-1; i>=0; i--) {
            if (indices[i] != i + n - r)
                break;
        }
        if (i==-1)
            return out;
        indices[i] += 1
        for (j=i+1; j<r; j++) {
            indices[j] = indices[j-1] + 1;
        }
        out.push( range(r).map(function(x){ return pool[indices[x]] }) )
    }
};

function range(start, stop) {
    if (typeof stop=='undefined') { stop = start; start = 0; };
    if (start >= stop) {
        return [];
    };
    var result = [];
    for (var i=start; i<stop; i+=1) {
        result.push(i);
    };
    return result;
};
