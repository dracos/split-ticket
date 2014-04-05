#!/usr/bin/env node
/*
 * TODO
 * Anytime return, not just off-peak
 * Going for the day? (CDR <-> two CDS)
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

var store = { data: {} };

// First, ask for from and to
/*
 * THIS DOES THE NICE STATION LOOKUP
Pprompt([
    { name: "from", message: "From", },
    { name: "to", message: "To", },
    // TIME
    // SAME DAY RETURN
])
.then(function(ans) {
    // Fetch the possibilities for those strings
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
*/
Q({ from: 'BHM', to: 'BRI' })
.then(function(ans) {
    store.from = ans.from;
    store.to = ans.to;
})
.then(function() {
    return [
        Pfetch('http://api.brfares.com/querysimple?orig=' + store.from + '&dest=' + store.to),
        Pfetch('http://traintimes.org.uk/' + store.from + '/' + store.to + '/10:00/monday'),
    ];
}).spread(function(fares, stops) {
    var re = /<a[^>]*href="(\/ajax-stoppingpoints[^"]*)">stops\/details/;
    var m = stops.match(re);
    if (m) {
        return [
            fares.fares.filter(function(s){ return s.ticket.code == 'SVR'; }),
            Pfetch('http://traintimes.org.uk' + m[1] + ';ajax=2'),
        ];
    } else {
        console.log(chalk.red("Could not get stops"));
        process.exit(1);
    }
}).spread(function(fares, stops) {
    var fare_total = fares[0].adult.fare,
        fare_total_s = chalk.blue(price(fare_total));
    console.log('Total fare is ' + fare_total_s);

 // var re = />.*? \[<abbr>[A-Z]{3}<\/abbr>/g;
    var re = /<abbr>[A-Z]{3}<\/abbr>/g;
    stops = stops.tables.reduce(function(a,b){ return a.concat(b.match(re)); }, []);
    stops = stops.map(function(x){ return x.substr(6, 3) });

    var all_stops = [ store.from ].concat(stops, store.to);
    all_stops.forEach(function(x){ store.data[x] = {}; });
    store.data[store.from][store.to] = fare_total;

    var stop_pairs = itertools.combination(all_stops, 2);
    stop_pairs = stop_pairs.filter(function(x){ return x[0] != store.from || x[1] != store.to; });

    function parse_fare(from, to) {
        return Pfetch('http://api.brfares.com/querysimple?orig=' + from + '&dest=' + to)
            .then(function(body) {
                var b = body.fares.filter(function(s){ return s.ticket.code.match(/SVR|CDR/); });
                if (!b.length) {
                    console.log(chalk.gray('-'));
                    return;
                }
                store.data[from][to] = b[0].adult.fare;
                console.log(chalk.gray(price(b[0].adult.fare)));
                return;
            });
    }

    var result = Q();
    stop_pairs.forEach(function(pair) {
        result = result.then(function() {
            process.stdout.write(chalk.gray('  Trying ' + pair[0] + '-' + pair[1]) + ': ');
            return parse_fare(pair[0], pair[1]);
        });
    });
    return result;
}).then(function() {
    // Okay, have all the prices, now for the magic algorithm
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

    console.log(chalk.black('Calculating shortest route...'));
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
        var f = nodes[i], t = nodes[i+1];
        console.log(f + ' ' + chalk.black('->') + ' ' + t + chalk.black(': ') + price(store.data[f][t]));
        total += store.data[f][t];
    }
    console.log(chalk.green('Total: ' + price(total)));
})
.then(function(){
    // Otherwise it seems to hang since I added redis request caching
    process.exit();
});
