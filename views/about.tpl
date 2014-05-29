% rebase('base.tpl')

<h2>About</h2>

<div class="front-col right">
<form action="/" method="get">

<p>
    <label for="from">From:</label>
    <input id="from" type="text" name="from" value="{{ get('from', '') }}">
</p>
<p>
    <label for="to">To:</label>
    <input id="to" type="text" name="to" value="{{ get('to', '') }}">
</p>
<p>
    <label for="time">Leave at:</label>
    <input id="time" type="text" name="time" placeholder="hh:mm" value="{{ get('time', '') }}">
</p>
<p>
    <label>For the day:</label>
    <label class="n"><input type="radio" name="day" value="y"{{ ' checked' if get('day')=='y' else '' }}> Yes</label>
    <label class="n"><input type="radio" name="day" value="n"{{ ' checked' if get('day')=='n' else '' }}> No</label>
</p>
<p align="right">
    <input type="submit" value="Search">
</p>
</form>
<script>
function search(id, placeholder) {
    $(id).autocomplete({
        serviceUrl: '/ajax-station',
        minChars: 2
    });
}
$(function(){
    search('#from');
    search('#to');
});
</script>
</div>

<h3>How is this possible?</h3>

<p>The railway’s national fares database is a very complicated affair, built up
over many years and dealing with an extraordinary array of restrictions and
conditions. This means that it is easily possible for two or more tickets to
act identically to one through ticket, but be substantially cheaper.

<p><a
href="http://www.railforums.co.uk/showpost.php?p=1179633&postcount=10">The
post on split ticketing in the RailUK Fares &amp; Ticketing Guide</a> is very
informative. Note there that using multiple tickets is explicitly permitted by
Section 19 of the National Rail Conditions of Carriage.

<p>Most importantly, if you buy multiple tickets (and aren’t using zonal/
season tickets), be sure that the train you catch stops at the station or
stations where you switch tickets. Otherwise your tickets will not be valid.

<p>Other than that, you can catch exactly the same trains, changing and
stopping at exactly the same places, as you would have done with a through
ticket. You don’t have to get off the train when you switch tickets :)

<h3>How does this site work?</h3>

<p>When you enter some journey details, it queries all the possible fares along
the journey, works out which tickets are valid at those times due to off-peak
restrictions and other factors, and then applies Dijkstra’s algorithm to find
the cheapest way through. You may then have to guide it to your own best
solution, by pointing out routes that you don’t want to take, or peak
restrictions you might need.

<h3>What doesn’t this site do?</h3>

<ul>

<li>Railcards – not just in terms of showing you prices, but e.g. if you
have a Network railcard or other non-national railcard, you might well want to
split at the boundary of the railcard to utilise its benefits.

<li>Advance tickets, which if you can stick to a precise train and are
available, will probably be cheaper. But note you can try splitting Advance
tickets too! Try looking up between major stations rather than your entire route;
again, RailUK has <a
href="http://www.railforums.co.uk/showpost.php?p=1179552&postcount=7">more
information on Advance quotas</a>.

<li>Journeys other than the one given for the time specified – I
might add a via option, as that would be straightforward to do.

<li>The time restrictions of your return journey – I thought it simplest to
deal with the morning restrictions, and then leave it to you to check your
return requirements based upon that.

<li>Definitely get everything right – it is more than likely that I
have miscoded something in my parsing of the national fares and timetable
databases, or misunderstood something in how ticket restrictions work. It has
given me useful and correct results for my own journeys, but if you find a
result that isn’t actually possible (it gives you a ticket which isn’t actually
valid for that train when you check), or it’s missing a cheaper result than
what it says, do let me know.

</ul>
