<h2>{{ fr_desc }} to {{ to_desc }},
% if via:
via {{ via }},
% end
% if day == 'y':
for the day,
% elif day == 'n':
return,
% end
leaving around {{ time }}
% if new_journey:
<br>
<a href="/">Enter new journey</a>
% end
</h2>
