#!/usr/bin/env node
/*
 * TODO
 * Anytime return, not just off-peak
 * Dijkstra of all the options...
 * Going for the day? (CDR <-> two CDS)
 */

"use strict";
var inquirer = require("inquirer"),
    chalk = require("chalk"),
    printf = require("printf"),
    request = require("request"),
    itertools = require("./itertools"),
    Q = require("q");

function Pprompt(qns) {
    var deferred = Q.defer();
    inquirer.prompt(qns, function(answers) { deferred.resolve(answers); });
    return deferred.promise;
}

function Pfetch(url) {
    var deferred = Q.defer();
    request({ url: url, json: true }, function(error, response, body) {
        if (error) { deferred.reject(new Error(error)); }
        else { deferred.resolve(body); }
    });
    return deferred.promise;
}

var store = {};

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
        throw new Error("Could not get stops");
    }
}).spread(function(fares, stops) {
    var fare_total = fares[0].adult.fare/100,
        fare_total_s = chalk.blue(printf('%.2f', fare_total));
    console.log('Total fare is ' + fare_total_s);

 // var re = />.*? \[<abbr>[A-Z]{3}<\/abbr>/g;
    var re = /<abbr>[A-Z]{3}<\/abbr>/g;
    stops = stops.tables.reduce(function(a,b){ return a.concat(b.match(re)); }, []);
    stops = stops.map(function(x){ return x.substr(6, 3) });

    var all_stops = [ store.from ].concat(stops, store.to);
    var stop_pairs = itertools.combination(all_stops, 2);
    stop_pairs = stop_pairs.filter(function(x){ return x[0] != store.from || x[1] != store.to; });

    var result = Q([]);
    stops.forEach(function(stop) {
        result = result.then(function(x){
            console.log(chalk.red(x[0]) + ' ' + chalk.blue(printf('%.2f', x[1]/100)) + ' + ' + chalk.blue(printf('%.2f', x[2]/100)));
            console.log('Trying ' + stop);
            return Q.all([
                stop,
                Pfetch('http://api.brfares.com/querysimple?orig=' + store.from + '&dest=' + stop)
                    .then(function(body) {
                        var b = body.fares.filter(function(s){ return s.ticket.code.match(/SVR|CDR/); });
                        if (!b.length) return -1;
                        return b[0].adult.fare;
                    }),
                Pfetch('http://api.brfares.com/querysimple?orig=' + stop + '&dest=' + store.to)
                    .then(function(body) {
                        var b = body.fares.filter(function(s){ return s.ticket.code.match(/SVR|CDR/); });
                        if (!b.length) return -1;
                        return b[0].adult.fare;
                    }),
            ]);
        });
    });
    return result;
}).then(function(x) {
    console.log(chalk.red(x[0]) + ' ' + chalk.blue(printf('%.2f', x[1]/100)) + ' + ' + chalk.blue(printf('%.2f', x[2]/100)));
});
;
