<!DOCTYPE html>
<html lang="en">
<head><title>{{ get('title', 'Split Ticket') }} - Accessible UK Train Timetables</title>
<link rel="stylesheet" href="/static/railway2.css">
<style>
/* Home */
input[type=text] {
    width: 80%;
}
.front-col {
    width: 45%;
    padding: 1em 2.5%;
    float: left;
}
.front-col > h2 {
    margin-top: 0;
}
label {
    display: block;
}
label.n { display: inline; }

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
<div style="position:fixed; top:0; left:0; right:0; background-color:#f00; color:#fff; padding:0.5em">
<em>&beta;</em> &mdash; In testing (it does now know the 08:55 Banbury&ndash;Reading off-peak return is off-peak)
</div>

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
