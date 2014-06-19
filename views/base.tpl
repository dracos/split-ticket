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

<script src='/bower_components/jquery/dist/jquery.min.js'></script>
<script src='/bower_components/devbridge-autocomplete/dist/jquery.autocomplete.min.js'></script>
<script src='//cdnjs.cloudflare.com/ajax/libs/jquery-color/2.1.2/jquery.color.min.js'></script>

<link rel="shortcut icon" href="http://traintimes.org.uk/favicon.ico">

<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="http://traintimes.org.uk/traintimes-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">

</head>

<body bgcolor="#ffffff" text="#000066" link="#0000ff" alink="#ff0000" vlink="#660066">

<div id="heading"><a id="home" href="/">sp<i>l</i>it.traintimes.org.uk</a>
<em>Beta</em>
<p id="credit"><i>by</i> <a href="http://dracos.co.uk/">Matthew</a>
&middot;&nbsp; <a id="donate" href="http://traintimes.org.uk/donate">Donate</a></p>
</div>

<div id="content">
{{ !base }}
</div>
<div style='clear:both'></div>
<p id="footer">
Timetable and Fares data available<br>
under a Creative Commons Attribution<br>
licence from RSP (thanks <a href="http://www.atoc.org/">ATOC</a>).<br>
Kindly hosted by <a href="http://www.bytemark.co.uk/">Bytemark</a>.

</p>

</body>
</html>
