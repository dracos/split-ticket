% rebase('base.tpl')

% include('heading.tpl', new_journey=False)

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
