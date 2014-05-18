<!DOCTYPE html>
<html lang="en">
<head><title>{{ get('title', 'Split Ticket') }} - Accessible UK Train Timetables</title>
<link rel="stylesheet" href="http://traintimes.org.uk/railway2.css">
<style>
label { white-space: nowrap; }

.autocomplete-suggestions { border: 1px solid #999; background: #FFF; overflow: auto; }
.autocomplete-suggestion { padding: 2px 5px; white-space: nowrap; overflow: hidden; cursor: pointer; }
.autocomplete-selected { background: #eeeeff; }
</style>

<script src='/bower/jquery/dist/jquery.min.js'></script>
<script src='/bower/devbridge-autocomplete/dist/jquery.autocomplete.min.js'></script>

<link rel="shortcut icon" href="http://traintimes.org.uk/favicon.ico">

<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="http://traintimes.org.uk/traintimes-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">

</head>

<body bgcolor="#ffffff" text="#000066" link="#0000ff" alink="#ff0000" vlink="#660066">
<div id="heading"><a id="home" href="/">sp<i>l</i>it.traintimes.org.uk</a>
<p id="credit"><em>by</em> <a href="http://www.dracos.co.uk/">Matthew</a>
&middot;&nbsp; <a id="donate" href="/donate">Donate</a></p>
</div>

<div id="content">
{{ !base }}
</div>
<div style='clear:both'></div>
<p id="footer">Kindly hosted by <a href="http://www.bytemark.co.uk/">Bytemark</a><br><a href="/terms"><small>Terms</small></a></p>

</body>
</html>
