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
<br>
<a href="/">Enter new journey</a>
</h2>

<div class="results">

<p>I’m afraid something went wrong and I couldn’t find any journey.
Please get in touch if you would like me to take a look at what went wrong.
Sorry about that.

</div>
