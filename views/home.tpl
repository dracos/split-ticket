% rebase('base.tpl')

<h2>Split ticket finder</h2>

<div class="hero">

<p>Say you&rsquo;re travelling from Bournville to Reading for the day, leaving
around 8am. If you just turned up and bought a ticket for that journey, it
would cost you &pound;103. Following this website,
<a href='/BRV/RDG/y/08:00'>it would only cost you <strong>&pound;32.70</strong></a>,
for the <em>same</em> journey on the <em>same</em> trains.
<a href="/about">More information...</a>

</div>

<div class="front-col">
% include('form')
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
                    if (el.find('li').length > 5) {
                        el.find('li').last().remove();
                    }
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
