<h2>{{ fr_desc }} to {{ to_desc }},
% if via:
via {{ via }},
% end
% if day == 'y':
for the day,
% elif day == 'n':
return,
% end
leaving around {{ time }}<!--
% if time_ret:
-->, returning around {{ time_ret }}<!--
% end
-->
% if new_journey:
<br>
<a href="/">Enter new journey</a>
% if time_ret:
&middot; <a href="/{{ get('from') }}/{{ to }}/{{ day }}/{{ time }}">Ignore return time</a>
% end
% end
</h2>
