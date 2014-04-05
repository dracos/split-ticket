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
    return printf('%.2f', n/100);
}

function parse_fare(from, to) {
    return Pfetch('http://api.brfares.com/querysimple?orig=' + from + '&dest=' + to)
    .then(function(body) {
        var b = body.fares.filter(function(s) {
            return 1 // s.category.desc == 'WALKUP'
            //    && s.route.name == 'ANY PERMITTED'
                && s.ticket.code.match(/SVR|SOR|CDR|SDR|CDS|SDS|SOS/);
        });
        var by_type = {};
        b.forEach(function(s) { by_type[s.ticket.code] = s; });
        var best = by_type.SVR || by_type.SOR;
        var double = false;
        if (store.day) {
            var best_day = by_type.CDR || by_type.SDR;
            if (!best || (best_day && best_day.adult.fare < best.adult.fare)) {
                best = best_day;
            }
        }
        if (!best) {
            best = by_type.CDS || by_type.SDS || by_type.SOS;
            double = true;
        }
        if (!best) {
            return '-';
        }
        var fare = best.adult.fare * (double?2:1);
        if (!(from in store.data)) store.data[from] = {};
        if (!(to in store.data)) store.data[to] = {};
        store.data[from][to] = fare;
        var disp = price(fare);
        if (double) disp += ' (2 singles)';
        return disp;
    });
}

var store = { data: {} };

// First, ask for from and to
Pprompt([
    { name: "from", message: "From", },
    { name: "to", message: "To", },
    { name: "day", message: "For the day", type: "confirm" },
])
.then(function(ans) {
    store.day = ans.day;
    if (!ans.from || !ans.to) {
        console.log(chalk.red("Please enter a From and a To"));
        process.exit(1);
    }

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
})
.then(function() {
    console.log(chalk.black('Looking up journey as a whole...'));
    return [
        parse_fare(store.from, store.to),
        Pfetch('http://traintimes.org.uk/' + store.from + '/' + store.to + '/10:00/monday'),
    ];
}).spread(function(fare_total, stops) {
    console.log('Total fare is', chalk.blue(fare_total));

    console.log(chalk.black('Fetching stopping points...'));

    var re = /<a[^>]*href="(\/ajax-stoppingpoints[^"]*)">stops/i;
    var m = stops.match(re);
    if (m) {
        return Pfetch('http://traintimes.org.uk' + m[1] + ';ajax=2');
    } else {
        console.log(chalk.red("Could not get stops"));
        process.exit(1);
    }
}).then(function(ints) {
    var stops = [], c = 0;
    ints.tables.forEach(function(x){
        stops = stops.concat(x.match(/<abbr>[A-Z]{3}/g).map(function(x){ return x.substr(6,3); }));
        stops.push( ints.destination[c++].match(/[A-Z]{3}/)[0] );
    });

    var all_stops = [ store.from ].concat(stops);
    console.log('Stations to consider:', chalk.gray(all_stops));

    console.log(chalk.black('Looking up all the pairwise fares...'));

    var stop_pairs = itertools.combination(all_stops, 2);
    stop_pairs = stop_pairs.filter(function(x){ return x[0] != store.from || x[1] != store.to; });

    var result = Q();
    stop_pairs.forEach(function(pair) {
        result = result.then(function(out) {
            if (out) console.log(chalk.gray(out));
            process.stdout.write(chalk.gray('  Trying ' + pair[0] + '-' + pair[1] + ': '));
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
            if (store.data[x][y] != -1) {
                graph.addEdge(x, y, store.data[x][y]);
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
        console.log(f + ' ' + chalk.gray('->') + ' ' + t + chalk.gray(': ') + price(d));
        total += d;
    }
    console.log(chalk.green('Total: ' + price(total)));
})
.then(function(){
    // Otherwise it seems to hang since I added redis request caching
    process.exit();
});
