#!/usr/bin/env node
/*
 * TODO
 * Anytime return, not just off-peak
 */

"use strict";
var inquirer = require("inquirer"),
    chalk = require("chalk"),
    printf = require("printf"),
    request = require("request"),
    RequestCaching = require("node-request-caching"),
    dijkstra = require("dijkstra"),
    itertools = require("./itertools"),
    Q = require("q");

var rc = new RequestCaching({
    store: 'redis',
    caching: { ttl: 86400, },
});

function Pprompt(qns) {
    var deferred = Q.defer();
    inquirer.prompt(qns, function(answers) { deferred.resolve(answers); });
    return deferred.promise;
}

function Pfetch(url) {
    var deferred = Q.defer();
    rc.request({ uri: url, }, function(error, response, body) {
        try { body = JSON.parse(body) } catch (e) {}
        if (error) { deferred.reject(new Error(error)); }
        else { deferred.resolve(body); }
    });
    return deferred.promise;
}

function price(n) {
    return printf('£%.2f', n/100).replace('.00', '');
}


function test_restriction(code, time) {
    if ([ '2V', 'G1', 'BX', 'GF' ].indexOf(code)>-1 && time >= '09:30') {
        return true;
    }
    if ([ 'W3' ].indexOf(code)>-1 && time >= '09:00') { // AND THE 08:59 TILEHURST TO OXFORD!
        return true;
    }
    if ([ 'W4' ].indexOf(code)>-1 && time >= '08:45') { // Additionally valid on the 08:41 departure from Swindon to Cheltenham Spa. 
        return true;
    }
    return false;
}

function parse_fare(from, to) {
    return Pfetch('http://api.brfares.com/querysimple?orig=' + from + '&dest=' + to)
    .then(function(body) {
        var b = body.fares.filter(function(s) { return s.ticket.code.match(/SVR|SOR|CDR|SDR|CDS|SDS|SOS/); });

        function fare_list(s) {
            var o = price(s.adult.fare);
            o += ' (' + prettify(s.ticket.name);
            if (s.route.name != 'ANY PERMITTED') o += ', ' + prettify(s.route.name)
            if (s.restriction_code != '  ') o += ', ' + s.restriction_code;
            o += ')';
            return o;
        }

        var returns = body.fares.filter(function(s) {
            var ret = s.ticket.code.match(/SVR|SOR/);
            if (store.day) {
                ret = ret || s.ticket.code.match(/CDR|SDR/);
            }
            return ret;
        });

        var best;
        returns.forEach(function(r){
            if (!best) { best = r; return; }
            if (r.adult.fare < best.adult.fare) {
                if (r.ticket.code == 'SOR' || r.ticket.code == 'SDR') {
                    best = r; return;
                }
                if (best.ticket.code == r.ticket.code && r.restriction_code == best.restriction_code) {
                    best = r; return;
                }
                if (from in store.departure_times) {
                    if (test_restriction(r.restriction_code, store.departure_times[from])) {
                        best = r; return;
                    }
                }
            }
        });

        var double = false;
        if (best) {
            process.stdout.write(returns.map(fare_list).join(' | ') + ' ');
        } else {
            var singles = body.fares.filter(function(s) { return s.ticket.code.match(/CDS|SDS|SOS/); });
            if (singles.length) {
                process.stdout.write(singles.map(fare_list).join(' | ') + ' ');
                best = singles[0];
                double = true;
            }
        }

        if (!best) {
            return '-';
        }

        var fare = best.adult.fare * (double?2:1);
        if (!(from in store.data)) store.data[from] = {};
        if (!(to in store.data)) store.data[to] = {};
        store.data[from][to] = { fare: fare, desc: fare_list(best) };
        var disp = price(fare);
        if (double) disp += ' (2 singles)';
        return disp;
    });
}

var store = { data: {}, departure_times: {} };

// First, ask for from and to
Pprompt([
    { default: 'BRV', name: "from", message: "From", validate: function(x) { if (x) return true; return false; } },
    { default: 'RDG', name: "to", message: "To", validate: function(x) { if (x) return true; return false; } },
    { name: "day", message: "For the day", type: "confirm" },
    { name: "time", message: "Departure time", default: "08:01",
        validate: function(x) { if (x.match(/^\d\d:\d\d$/)) return true; return false; }
    },
])
.then(function(ans) {
    store.day = ans.day;
    store.time = ans.time;

    console.log(chalk.black('Looking up entered terms...'));

    return [
        Pfetch('http://api.brfares.com/ac_loc?term=' + encodeURIComponent(ans.from)),
        Pfetch('http://api.brfares.com/ac_loc?term=' + encodeURIComponent(ans.to))
    ];
}).spread(function(from, to) {
    var modify = function(x) { x.name = x.value; x.value = x.code; },
        qns;
    from.forEach(modify);
    to.forEach(modify);
    if (from.length > 1) {
        qns = [ { type: "list", name: "from", message: "From choice", choices: from, } ];
        from = Pprompt(qns);
    } else {
        from = Q({ 'from': from[0].code });
    }
    return from.then(function(from) {
        if (to.length > 1) {
            qns = [ { type: "list", name: "to", message: "To choice", choices: to, } ];
            to = Pprompt(qns);
        } else {
            to = Q({ 'to': to[0].code });
        }
        return [ from, to ];
    });
})
.spread(function(from, to) {
    store.from = encodeURIComponent(from.from);
    store.to = encodeURIComponent(to.to);
    store.departure_times[store.from] = store.time;
})
.then(function() {
    console.log(chalk.black('Looking up journey as a whole...'));
    return [
        parse_fare(store.from, store.to),
        Pfetch('http://traintimes.org.uk/' + store.from + '/' + store.to + '/' + store.time + '/monday'),
    ];
}).spread(function(fare_total, stops) {
    console.log('\nTotal fare is', chalk.blue(fare_total));

    console.log(chalk.black('Fetching stopping points...'));

    var re = /<li id="result0">[\s\S]*?<li id="result1">/, m;
    if (m = stops.match(re)) {
        var res1 = m[0];
        re = /<strong>.*?(\d\d:\d\d) /;
        if (m = res1.match(re)) {
            store.departure_times[store.from] = m[1];
        }
        re = /<td>(\d\d:\d\d)<\/td>\s*<td class="origin">.*?<abbr>([A-Z]{3})/g;
        if (m = res1.match(re)) {
            m = m.map(function(x){
                var q = x.match(/<td>(\d\d:\d\d)<\/td>\s*<td class="origin">.*?<abbr>([A-Z]{3})/);
                store.departure_times[q[2]] = q[1];
            });
        }
    }

    re = /<a[^>]*href="(\/ajax-stoppingpoints[^"]*)">stops/i;
    if (m = stops.match(re)) {
        return Pfetch('http://traintimes.org.uk' + m[1] + ';ajax=2');
    } else {
        console.log(chalk.red("Could not get stops"));
        process.exit(1);
    }
}).then(function(ints) {
    var stops = [], c = 0;
    ints.tables.forEach(function(x){
        stops = stops.concat((x.match(/<abbr>[A-Z]{3}/g)||[]).map(function(x){ return x.substr(6,3); }));
        stops.push( ints.destination[c++].match(/[A-Z]{3}/)[0] );
    });
    for (var i in ints.parsed) { store.departure_times[i] = ints.parsed[i]; }

    var all_stops = [ store.from ].concat(stops);
    console.log('Stations to consider:', chalk.gray(all_stops));

    console.log(chalk.black('Looking up all the pairwise fares...'));

    var stop_pairs = itertools.combination(all_stops, 2);
    stop_pairs = stop_pairs.filter(function(x){ return x[0] != store.from || x[1] != store.to; });

    var result = Q();
    stop_pairs.forEach(function(pair) {
        result = result.then(function(out) {
            if (out) console.log(chalk.gray(out));
            process.stdout.write(chalk.gray(pair[0] + '-' + pair[1] + ': '));
            return parse_fare(pair[0], pair[1]);
        });
    });
    return result;
}).then(function(out) {
    if (out) console.log(chalk.gray(out));

    // Okay, have all the prices, now for the magic algorithm
    console.log(chalk.black('Calculating shortest route...'));

    var graph = new dijkstra.Graph();
    Object.keys(store.data).forEach(function(x){
        graph.addVertex(x);
    });
    Object.keys(store.data).forEach(function(x){
        Object.keys(store.data[x]).forEach(function(y){
            if (store.data[x][y].fare != -1) {
                graph.addEdge(x, y, store.data[x][y].fare);
            }
        });
    });

    var result = dijkstra.dijkstra(graph, store.from);
    var node = store.to;
    var nodes = [];
    while (node) {
        nodes.push(node);
        node = result[JSON.stringify(node)];
    }
    nodes.reverse();
    var total = 0;
    for (i=0; i<nodes.length-1; i++) {
        var f = nodes[i], t = nodes[i+1],
            d = store.data[f][t];
        console.log(f + ' ' + chalk.gray('->') + ' ' + t + chalk.gray(': ') + d.desc);
        total += d.fare;
    }
    console.log(chalk.green('Total: ' + price(total)));
})
.then(function(){
    // Otherwise it seems to hang since I added redis request caching
    process.exit();
});

function prettify(s) {
    return s
        .replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();})
        .replace(/ R$/, ' Return')
        .replace(/ S$/, ' Single')
}
