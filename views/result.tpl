% rebase('base.tpl')
% from split.utils import price

<h2>{{ fr_desc }} to {{ to_desc }},
% if day:
for the day,
% end
leaving around {{ time }}
</h2>

<p><span style="font-size: 200%">The normal fare is <strong>{{ price(fare_total['fare']) }}</strong></span>
({{ fare_total['desc'] }})</p>

<p style="font-size: 200%">But I&rsquo;ve found the same journey for&hellip; <strong>{{ price(total) }}</strong></p>

<ol style="font-size: 120%">
% for step in output_cheapest:
<li>{{ step[0] }} &rarr; {{ step[1] }} : {{ price(step[2]['fare']) }} ({{ step[2]['desc'] }})</li>
% end
</ol>

% if routes:
<div style="float: left; width:40%; margin-right:10%">
<p>The above may not be the most obvious route due to route selection, exclude a route using the links below:</p>
<ul>
% for id, route in routes.items():
<li><a href="?exclude={{ ','.join(set(exclude + [ id ])) }}">{{ route['name'].title() }}</a>
% end
</ul>
</div>
% end

<div style="float: left; width: 50%">
<p>I considered the following journey:</p>
% for stop in all_stops_with_depart:
<div style="float:left; width: 4em; height: 4em; text-align:center; background-color:#eeeeff; margin: 0.25em; padding: 0.25em;">
{{ stop[0] }}<br>
% if stop[1][0] and stop[1][0] != stop[1][1]:
{{ stop[1][0] }}a{{ ',' if stop[1][1] else '' }}
% end
{{ stop[1][1] or '' }}{{ 'd' if stop[1][1] and stop[1][0] and stop[1][0] != stop[1][1] else '' }}
</div>
% end
</div>
<div style="clear:both"></div>

<h3 id="working-out" style="cursor:pointer">My working out</h3>
<ul id="js-working-out">
% for pair in output_pairwise:
<li>{{ pair[0] }}&ndash;{{ pair[1] }}, {{ price(pair[2]['fare']) }} {{ pair[2]['desc'] }}</li>
% end
</ul>
<script>
$(function(){
    $('#working-out').click(function(){ $('#js-working-out').slideToggle(); });
    $('#js-working-out').hide();
});
</script>
