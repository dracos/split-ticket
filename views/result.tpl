% rebase('base.tpl')
% from split.utils import price

<h2>{{ fr_desc }} to {{ to_desc }},
% if via:
via {{ via }},
% end
% if day:
for the day,
% end
leaving around {{ time }}
</h2>

<div class="results">

<p><span class="imp">The normal fare is <strong>{{ price(fare_total['fare']) }}</strong></span>
<span class="faded">{{ !fare_total['desc'] }}</span></p>

% if total < fare_total['fare']:
<p class="imp">But I&rsquo;ve found the same journey for&hellip; <strong>{{ price(total) }}</strong></p>

<ol>
% for step in output_cheapest:
<li>{{ step[0] }} &rarr; {{ step[1] }} : {{ price(step[2]['fare']) }}
<br><small class="faded">{{ !step[2]['desc'] }}</small></li>
% end
</ol>
% else:
<p>And I&rsquo;m afraid I didn&rsquo;t find any split that made it cheaper.</p>
% end

</div>


% if routes or restrictions:
<div class="results-text">

% if get('skipped_problem_routes'):
<p class="info">There are cheaper options available, but would involve you
taking a different route. <a href="?all=1">See all options</a>, starting with
the cheapest.</p>
% end

<p>The above may not be the best route <strong>for you</strong>, and in fact
<strong>may not be valid</strong> (my lookup doesn’t account for all
via/operator restrictions). <strong>Check.</strong> I also don’t account for
return times, so you may need to adjust if you’re returning in a peak period.

% if routes:

Exclude a particular route or restriction using the links
below:</p>

<ul>
% for route in routes:
<li><a href="?{{ 'all=1;' if all else '' }}exclude={{ ','.join(set(exclude + [ route['id'] ])) }}">Exclude {{ route['desc'].title() }}</a>
% end
</ul>
% end

% if restrictions:
<p>Ignore tickets with time restriction:
<ul>
% for id, text in restrictions.items():
<li><a href="?{{ 'all=1;' if all else '' }}exclude={{ ','.join(set(exclude + [ id ])) }}">({{ id}}) {{ text }}</a>
% end
</ul>
% end

<p>
Please note that your train <strong>must stop</strong> at the stations on your
tickets in order to be valid. This site does not look at Advance tickets,
rovers, or anything odd or special. E&amp;OE, <strong>check your tickets and
their restrictions</strong> before purchasing. <a href="/about">More information</a>
</p>

</div>
% end

<div class="stop-list">
<p>I considered the following journey
(<a href="http://traintimes.org.uk/{{ fr }}/{{ to }}/{{ time }}/next-tuesday">check
on traintimes.org.uk</a> to adjust search time):</p>
% for code, chg, stop, times in all_stops_with_depart:
<div class="stop{{ ' chg' if chg else '' }}">
<abbr title="{{ stop['description'] }}{{ ', changing' if chg else '' }}">{{ code }}</abbr><br>
% if times[0] and times[0] != times[1]:
{{ times[0] }}a{{ ',' if times[1] else '' }}
% end
{{ times[1] or '' }}{{ 'd' if times[1] and times[0] and times[0] != times[1] else '' }}
</div>
%     if stop != all_stops_with_depart[-1][2]:
<div class="stop-arrow"> &rarr; </div>
%     end
% end
</div>

<p><a id='working-out-link' href='#working-out'>See the intermediate fares</a> used for the above calculation:</p>
<ul id="working-out">
% for pair in output_pairwise:
<li>{{ pair[0] }}&ndash;{{ pair[1] }}, {{ price(pair[2]['fare']) }}
<small><span class="faded">{{ !pair[2]['desc'] }}</span></small></li>
% end
</ul>
<script>
$(function(){
    $('#working-out-link').click(function(){ $('#working-out').slideToggle(); return false; });
    $('#working-out').hide();
});
</script>
