% rebase('base.tpl')

<h2>Split ticket finder</h2>

<div class="hero" style="font-size:120%; margin-bottom:1em; padding:1em">
<p>I&rsquo;ve got a local copy of the fares database,
which means I can query it for a number of possibilities
that might give you a cheaper ticket.</p>

<p>For example, imagine you wanted to go from <a href='?from=BRV&amp;to=RDG&amp;time=08:00&amp;day=y&amp;exclude=00046'>Bournville to Reading for the day, leaving at 08:00</a>? Follow that link to see how you can save <strong>&pound;70</strong>!</p>
</div>

<form>
<p>
    <input id="from" type="hidden" name="from" value="{{ get('from', '') }}" data-desc="{{ get('from_desc', '') }}">
    <input id="to" type="hidden" name="to" value="{{ get('to', '') }}" data-desc="{{ get('to_desc', '') }}">
<p>
    Departure time: <input type="text" name="time" placeholder="hh:mm" value="{{ get('time', '') }}">
    <input type="checkbox" name="day" value="y"{{ ' checked' if get('day') else '' }}> For the day
<p>
    <input type="submit" value="Investigate">
</form>
<script>
function search(id, placeholder) {
    $(id).select2({
        minimumInputLength: 2,
        placeholder: placeholder,
        width: '40%',
        ajax: {
            url: '/ajax-station',
            dataType: 'json',
            data: function(term, page) { return { q: term }; },
            results: function(data, page) { return data; }
        },
        initSelection: function(element, callback) {
            callback({ id: element.val(), text: element.data('desc') || element.val() });
        }
    });
}
search('#from', 'From station');
search('#to', 'To station');
</script>

