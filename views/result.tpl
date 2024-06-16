% rebase('base.tpl', nofollow=True)
% from split.utils import price

% include('heading.tpl', new_journey=True)

<div class="results">

% if get('skipped_problem_routes') and not exclude and total >= fare_total['fare']:
<p class="info">I also found cheaper options, that <em>might</em> (but might
not) involve you taking a different route.
<a href="?{{ 'via=' + via + '&' if via else '' }}all=1">See all options</a>,
starting with the cheapest.</p>
% end

% if fare_total['fare'] == '-':
<p><span class="imp">I couldn’t find a valid through ticket for this journey; perhaps try a different time?</span></p>
% else:
<div><span class="imp">The normal weekday fare is <strong>{{ price(fare_total['fare']) }}</strong></span>
<div class="faded">{{ !fare_total['desc'] }}</div>
</div>
% end

% if total < fare_total['fare']:
<p class="imp">But I&rsquo;ve found the same journey for&hellip; <strong>{{ price(total) }}</strong></p>

% if get('skipped_problem_routes') and not exclude:
<p class="info">I also found cheaper options, that <em>might</em> (but might
not) involve you taking a different route.
<a href="?{{ 'via=' + via + '&' if via else '' }}all=1">See all options</a>,
starting with the cheapest.</p>
% end

<ol>
% for step in output_cheapest:
<li>{{ step[0] }} {{ ! '&rarr;' if day == 's' else '&harr;' }} {{ step[1] }} : {{ price(step[2]['fare']) }}
<div class="faded">{{ !step[2]['desc'] }}</div></li>
% end
</ol>
% else:
<p>And I&rsquo;m afraid I didn&rsquo;t find any split that made it cheaper.</p>
% end

</div>

<div class="results-text">

<p>The above may not be the best route, and may not be valid (I might not have
understood a particular restriction).
% if time_ret:
Adjusting your times may give cheaper results,
as different trains stop at different stations
offering different splitting options.
% else:
It doesn’t account for return times, so you may need to adjust the result if
you’re returning in a peak period.
% end

% if routes:

Exclude a particular route or restriction using the links
below:</p>

<ul>
% for route in routes:
<li><a href="?{{ 'all=1&' if all else '' }}{{ 'via=' + via + '&' if via else '' }}exclude={{ ','.join(set(exclude + [ route['id'] ])) }}">Exclude {{ route['desc'].title() }}</a>
% end
</ul>
% end

% if restrictions:
<p>Ignore tickets with time restriction:
<ul>
% for id, text in restrictions.items():
<li><a href="?{{ 'all=1&' if all else '' }}{{ 'via=' + via + '&' if via else '' }}exclude={{ ','.join(set(exclude + [ id ])) }}">(code {{ id }}) {{ text }}</a>
% end
</ul>
% end

<p>Don’t try and split at a particular station (if e.g. you
know return trains are unlikely to stop there):
<ul>
% for i, stop in enumerate(stops_joint):
%   if i == 0 or i == len(stops_joint)-1:
%     continue
%   end
<li><a href="?{{ 'all=1&' if all else '' }}{{ 'via=' + via + '&' if via else '' }}exclude={{ ','.join(set(exclude + [ stop.code ])) }}">Exclude {{ stop.desc }}</a>
% end
</ul>

</div>

<div class="stop-list">
<p>
Your train <strong>must stop</strong> at the stations on your tickets in order
to be valid. Check your tickets and their restrictions!
<a href="/about">More information</a>
</p>

<hr>

<p>I considered the following journey
(<a href="https://traintimes.org.uk/{{ get('from') }}/{{ to }}/{{ time }}/next-tuesday{{ '?via=' + via if via else '' }}">check
on traintimes.org.uk</a> to adjust search time):</p>
% for stop in stops:
<div class="stop{{ ' chg' if stop.change else '' }}">
<abbr title="{{ stop.desc }}{{ ', changing' if stop.change and stop != stops[0] and stop != stops[-1] else '' }}">{{ stop.code }}</abbr><br>
% if stop.times[0] and stop.times[0] != stop.times[1]:
{{ stop.times[0] }}a{{ ',' if stop.times[1] else '' }}
% end
{{ stop.times[1] or '' }}{{ 'd' if stop.times[1] and stop.times[0] and stop.times[0] != stop.times[1] else '' }}
</div>
%     if stop != stops[-1]:
<div class="stop-arrow"> &rarr; </div>
%     end
% end

% if time_ret:
<br clear="both">
And the following return journey
(<a href="https://traintimes.org.uk/{{ to }}/{{ get('from') }}/{{ time_ret }}/{{ 'next-tuesday' if day == 'y' else 'next-wednesday' }}{{ '?via=' + via if via else '' }}">check
on traintimes.org.uk</a>):</p>
%   for stop in stops_ret:
<div class="stop{{ ' chg' if stop.change else '' }}">
<abbr title="{{ stop.desc }}{{ ', changing' if stop.change and stop != stops_ret[0] and stop != stops_ret[-1] else '' }}">{{ stop.code }}</abbr><br>
%     if stop.times[0] and stop.times[0] != stop.times[1]:
{{ stop.times[0] }}a{{ ',' if stop.times[1] else '' }}
%     end
{{ stop.times[1] or '' }}{{ 'd' if stop.times[1] and stop.times[0] and stop.times[0] != stop.times[1] else '' }}
</div>
%     if stop != stops_ret[-1]:
<div class="stop-arrow"> &rarr; </div>
%     end
%   end
% end
</div>
