<!DOCTYPE html>
<html lang="en">
<head><title>{{ get('title', 'Split Ticket') }} - Accessible UK Train Timetables</title>
<link rel="stylesheet" href="/static/railway2.css">
<link rel="stylesheet" href="/static/split.css">
% if get('refresh'):
<noscript>
<meta http-equiv="refresh" content="{{ refresh }}; url={{ url_job }}">
</noscript>
% end
% if get('nofollow'):
<meta name="robots" content="nofollow">
% end
% if get('noindex'):
<meta name="robots" content="noindex,nofollow">
% end

<script src='/static/jquery-3.6.0.min.js'></script>
<script src='/static/jquery.autocomplete.min.js'></script>
<script src='//cdnjs.cloudflare.com/ajax/libs/jquery-color/2.1.2/jquery.color.min.js'></script>

<link rel="shortcut icon" href="https://traintimes.org.uk/favicon.ico">

<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="https://traintimes.org.uk/traintimes-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="google-site-verification" content="UTtqZo2AeTn8Cq6meBghyrJeIJN7C7E9uuAZbB7LZ5Q">

% if get('fare_total') and fare_total['fare'] != '-' and total < fare_total['fare']:
% import re
<meta property="twitter:card" content="summary">
<meta property="twitter:site" content="@dracos">
<meta property="twitter:title" content="Split ticket finder, {{ fr_desc }} to {{ to_desc }}">
<meta property="twitter:description" content="The normal weekday fare is {{ price(fare_total['fare']) }} ({{ re.sub('<[^>]*>', '', fare_total['desc']) }}), but I’ve found the same journey for {{ price(total) }}.
% if day == 's':
One way,
% elif day == 'y':
Going for the day,
% elif day == 'n':
Return,
% end
% if via:
via {{ via }},
% end
leaving around {{ time }}
% if time_ret and day != 's':
and returning around {{ time_ret }}
% end
">
% elif get('latest'):
<meta property="twitter:card" content="summary">
<meta property="twitter:site" content="@dracos">
<meta property="twitter:title" content="Split ticket finder">
<meta property="twitter:description" content="Bournville to Reading for the day, leaving at 8am, costs £128.30 on the day. Buy two tickets, still on the day, and it’s only £38.60 – same journey, same trains.">
% end

</head>

<body bgcolor="#ffffff" text="#000066" link="#0000ff" alink="#ff0000" vlink="#660066">

<div id="heading"><a id="home" href="/">sp<i>l</i>it.traintimes.org.uk</a>
<p id="credit"><i>by</i> <a href="http://dracos.co.uk/">Matthew</a>
&middot;&nbsp; <a id="donate" href="https://traintimes.org.uk/donate">Donate</a></p>
</div>

<!--
<div id="advert">
I&rsquo;m afraid this site is currently not working, due to issues
with traintimes.org.uk.
</div>
-->

<div id="content">
{{ !base }}
</div>
<div style='clear:both'></div>
<p id="footer">
Timetable and Fares data available<br>
under a Creative Commons Attribution<br>
licence from RSP (thanks <a href="https://www.raildeliverygroup.com/">Rail Delivery Group</a>).<br>
Kindly hosted by <a href="https://www.mythic-beasts.com/">Mythic Beasts</a>.

</p>

</body>
</html>
