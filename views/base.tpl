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

.error {
    color: #990000;
}

.autocomplete-suggestions { border: 1px solid #999; background: #FFF; overflow: auto; }
.autocomplete-suggestion { padding: 2px 5px; white-space: nowrap; overflow: hidden; cursor: pointer; }
.autocomplete-selected { background: #eeeeff; }
</style>

<script src='/bower/jquery/dist/jquery.min.js'></script>
<script src='/bower/devbridge-autocomplete/dist/jquery.autocomplete.min.js'></script>
<script src='//cdnjs.cloudflare.com/ajax/libs/jquery-color/2.1.2/jquery.color.min.js'></script>

<link rel="shortcut icon" href="http://traintimes.org.uk/favicon.ico">

<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="http://traintimes.org.uk/traintimes-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">

</head>

<body bgcolor="#ffffff" text="#000066" link="#0000ff" alink="#ff0000" vlink="#660066">
<div style="position:fixed; top:0; left:0; background-color:#f00; color:#fff; padding:0.5em">
<em>&beta;</em>
</div>

<div id="heading"><a id="home" href="/">sp<i>l</i>it.traintimes.org.uk</a>
<p id="credit"><em>by</em> <a href="http://www.dracos.co.uk/">Matthew</a>
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
