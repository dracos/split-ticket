% rebase('base.tpl')

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

<p>I&rsquo;m just doing the calculations&hellip;
% if queue_size == 1:
(there is one other currently being processed)
% elif queue_size:
(there are {{ queue_size }} others currently being processed)
% end
</p>
<p><img src="/static/animated.gif" width=500 height=281 alt=""></p>
</div>
