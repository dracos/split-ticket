% rebase('base.tpl')
% from split.utils import price

<h2>{{ fr_desc }} to {{ to_desc }},
% if day:
for the day,
% end
leaving around {{ time }}
</h2>

<div style="margin-bottom: 1em; font-size:120%">

<p><span style="font-size: 150%">The normal fare is <strong>{{ price(fare_total['fare']) }}</strong></span>
<span style="color:#999">{{ fare_total['desc'] }}</span></p>

% if total < fare_total['fare']:
<p style="font-size: 150%">But I&rsquo;ve found the same journey for&hellip; <strong>{{ price(total) }}</strong></p>

<ol>
% for step in output_cheapest:
<li>{{ step[0] }} &rarr; {{ step[1] }} : {{ price(step[2]['fare']) }}
<br><small style="color:#999">{{ step[2]['desc'] }}</small></li>
% end
</ol>
% else:
<p>And I&rsquo;m afraid I didn&rsquo;t find any split that made it cheaper.</p>
% end

</div>


% if routes or restrictions:
<div style="float: left; width:40%; margin-right:10%">

<p>The above may not be the best route, I just pick the cheapest. I also don't
account for return times, so you may need to adjust if you're returning in a peak period. Exclude
a particular route or restriction using the links below:</p>

<ul>
% for id, route in routes.items():
<li><a href="?exclude={{ ','.join(set(exclude + [ id ])) }}">Exclude {{ route['name'].title() }}</a>
% end
</ul>

<ul>
% for r in restrictions.keys():
<li><a href="?exclude={{ ','.join(set(exclude + [ r ])) }}">Ignore {{ r }} restricted tickets</a>
% end
</ul>
</div>
% end

<div style="float: right; width: 50%">
<p>I considered the following journey:</p>
% for code, stop, times in all_stops_with_depart:
<div style="float:left; width: 4em; height: 4em; text-align:center; background-color:#eeeeff; margin: 0.25em; padding: 0.25em;">
<abbr title="{{ stop['description'] }}">{{ code }}</abbr><br>
% if times[0] and times[0] != times[1]:
{{ times[0] }}a{{ ',' if times[1] else '' }}
% end
{{ times[1] or '' }}{{ 'd' if times[1] and times[0] and times[0] != times[1] else '' }}
</div>
<div style="float:left; padding: 1.5em 0 0;"> &rarr; </div>
% end
</div>

<p>
Please note that your train <strong>must stop</strong> at the stations on your
tickets in order to be valid. This site does not look at Advance tickets, rovers,
or anything odd or special. E&amp;OE, source code is
<a href="https://github.com/dracos/split-ticket">on GitHub</a>.
</p>

<p><a id='working-out-link' href='#working-out'>See the intermediate fares</a> used for the above calculation:</p>
<ul id="working-out">
% for pair in output_pairwise:
<li>{{ pair[0] }}&ndash;{{ pair[1] }}, {{ price(pair[2]['fare']) }}
<small><span style="color:#999">{{ pair[2]['desc'] }}</span></small></li>
% end
</ul>
<script>
$(function(){
    $('#working-out-link').click(function(){ $('#working-out').slideToggle(); return false; });
    $('#working-out').hide();
});
</script>
