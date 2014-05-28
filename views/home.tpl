% rebase('base.tpl')

<h2>Split ticket finder</h2>

<div class="hero" style="font-size:120%; padding:1em; background-color: #006; color: #eef;">

<p>Say you&rsquo;re travelling from Bournville to Reading for the day, leaving
around 8am. If you just turned up and bought a ticket for that journey, it
would cost you &pound;103. Following this website,
<a style="color: #ccf" href='/BRV/RDG/y/08:00?exclude=00046'>it would only cost you <strong>&pound;32.70</strong></a>,
for the <em>same</em> journey on the <em>same</em> trains.

</div>

<div class="front-col">
<form action="/" method="get" style="margin: -1em 0 0; border: solid 0px #006; border-top: none; padding: 1em; background-color: #eef;">

<p{{ !' class="error"' if errors.get('from') else '' }}>
    <label for="from">{{ errors.get('from', 'From') }}:</label>
    <input id="from" type="text" name="from" value="{{ get('from', '') }}">
</p>
<p{{ !' class="error"' if errors.get('to') else '' }}>
    <label for="to">{{ errors.get('to', 'To') }}:</label>
    <input id="to" type="text" name="to" value="{{ get('to', '') }}">
</p>
<p{{ !' class="error"' if errors.get('time') else '' }}>
    <label for="time">{{ errors.get('time', 'Leave at') }}:</label>
    <input id="time" type="text" name="time" placeholder="hh:mm" value="{{ get('time', '') }}">
</p>
<p{{ !' class="error"' if errors.get('day') else '' }}>
    <label>{{ errors.get('day', 'For the day') }}:</label>
    <label class="n"><input type="radio" name="day" value="y"{{ ' checked' if get('day')=='y' else '' }}> Yes</label>
    <label class="n"><input type="radio" name="day" value="n"{{ ' checked' if get('day')=='n' else '' }}> No</label>
</p>
<p align="center">
    <input type="submit" value="Search" style="font-size:1.5em;color:#000;background-color:#eee">
</p>
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
</div>

<div class="front-col">
% if latest:
<h2>Latest findings</h2>
<ul id='latest'>
%   for l in latest:
%     if l:
<li>{{ !l }}</li>
%     end
%   end
</ul>
<script>
$(function(){
    function fetchLatest() {
        $.get('/ajax-latest', function(data) {
            var a = data.latest,
                el = $('#latest'),
                existing = el.find('li').map(function(i, el) { return $(el).html(); }).get(),
                i, n;
            for (i=0; i<a.length; i++) {
                if ($.inArray(a[i], existing) === -1) {
                    n = $('<li/>').html(a[i]);
                    el.prepend(n);
                    n.css({backgroundColor: '#ffc'}).animate({backgroundColor:'#fff'}, 1500);
                    el.find('li').last().remove();
                }
            }
            setTimeout(fetchLatest, 5000);
        });
    }
    setTimeout(fetchLatest, 5000);
});
</script>
% end
</div>
