% rebase('base.tpl')
% from split.utils import price

<h2>{{ fr_desc }} to {{ to_desc }},
% if day:
for the day,
% end
leaving around {{ time }}
</h2>

<div style="margin-bottom: 2em; font-size:120%">

<p><span style="font-size: 150%">The normal fare is <strong>{{ price(fare_total['fare']) }}</strong></span>
({{ fare_total['desc'] }})</p>

% if total < fare_total['fare']:
<p style="font-size: 150%">But I&rsquo;ve found the same journey for&hellip; <strong>{{ price(total) }}</strong></p>

<ol>
% for step in output_cheapest:
<li>{{ step[0] }} &rarr; {{ step[1] }} : {{ price(step[2]['fare']) }} ({{ step[2]['desc'] }})</li>
% end
</ol>
% else:
<p>And I&rsquo;m afraid I didn&rsquo;t find any split that made it cheaper.</p>
% end

</div>


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
% end
</div>

<p><a id='working-out-link' href='#working-out'>See the intermediate fares</a> used for the above calculation:</p>
<ul id="working-out">
% for pair in output_pairwise:
<li>{{ pair[0] }}&ndash;{{ pair[1] }}, {{ price(pair[2]['fare']) }} {{ pair[2]['desc'] }}</li>
% end
</ul>
<script>
$(function(){
    $('#working-out-link').click(function(){ $('#working-out').slideToggle(); return false; });
    $('#working-out').hide();
});
</script>
