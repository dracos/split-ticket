% rebase('base.tpl')
% from split.utils import price

<h2>{{ fr }} to {{ to }},
% if day:
for the day,
% end
leaving at {{ time }}
</h2>

<p><span style="font-size: 200%">The normal fare is <strong>{{ price(fare_total['fare']) }}</strong></span>
({{ fare_total['desc'] }})</p>

<p style="font-size: 200%">But I&rsquo;ve found the same journey for&hellip; <strong>{{ price(total) }}</strong></p>

<ul>
% for step in output_cheapest:
<li>{{ step[0] }} &rarr; {{ step[1] }} : {{ price(step[2]['fare']) }} ({{ step[2]['desc'] }})</li>
% end
</ul>

<p>Routes you might want to exclude, the above might not be the most obvious way:</p>
% if routes:
<ul>
% for route in routes:
<li><a href="">{{ route.title() }}</a>
% end
</ul>
% end

<p>I considered the following journey:
<br>{{ ', '.join(all_stops_with_depart) }}</p>

<h3>My working out</h3>
<ul>
% for pair in output_pairwise:
<li>{{ pair[0] }}&ndash;{{ pair[1] }} ({{ pair[2] }}), {{ price(pair[3]['fare']) }} {{ pair[3]['desc'] }}</li>
% end
</ul>


