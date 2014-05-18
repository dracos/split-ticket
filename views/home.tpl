% rebase('base.tpl')

<h2>Split ticket finder</h2>

<div class="hero" style="font-size:150%; padding:0.5em">

<p>You&rsquo;re travelling from Bournville to Reading for the day, leaving around 8am.
If you just turned up and bought a ticket for that journey, it would cost you
<strong>&pound;103</strong>. Following this website,
<a href='/BRV/RDG/y/08:00?exclude=00046'>it would only cost you <strong>&pound;32.70</strong></a>,
for the same journey on the same trains.

</div>

<form action="/" method="get">
<p>
    <label>From: <input id="from" type="text" name="from" value="{{ get('from', '') }}" data-desc="{{ get('from_desc', '') }}"></label>
    <label>To: <input id="to" type="text" name="to" value="{{ get('to', '') }}" data-desc="{{ get('to_desc', '') }}"></label>
<p>
    <label>Departure time: <input type="text" name="time" placeholder="hh:mm" value="{{ get('time', '') }}"></label>
    For the day: <label><input type="radio" name="day" value="y"{{ ' checked' if get('day')=='y' else '' }}> Yes</label>
    <label><input type="radio" name="day" value="n"{{ ' checked' if get('day')=='n' else '' }}> No</label>
    <input type="submit" value="Search" style="font-size:1.5em;color:#000;background-color:#eee">
</form>
<script>
function search(id, placeholder) {
    $(id).autocomplete({
        serviceUrl: '/ajax-station',
        minChars: 2
    });
}
$(function(){
    search('#from');
    search('#to');
});
</script>

% if latest:
<h2>Latest findings</h2>
<ul>
%   for l in latest:
%     if l:
<li>{{ !l }}
%     end
%   end
</ul>
% end
