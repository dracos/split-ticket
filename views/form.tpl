<form action="/" method="get">

<p{{ !' class="error"' if errors.get('from') else '' }}>
    <label for="from">{{ errors.get('from', 'From') }}:</label>
    <input class='ac' id="from" type="text" name="from" value="{{ get('from', '') }}">
</p>
<p{{ !' class="error"' if errors.get('to') else '' }}>
    <label for="to">{{ errors.get('to', 'To') }}:</label>
    <input class='ac' id="to" type="text" name="to" value="{{ get('to', '') }}">
</p>
<p{{ !' class="error"' if errors.get('via') else '' }}>
    <label for="via">{{ errors.get('via', 'Via') }}: (optional)</label>
    <input class='ac' id="via" type="text" name="via" value="{{ get('via', '') }}">
</p>
<p{{ !' class="error"' if errors.get('time') else '' }}>
    <label for="time">{{ errors.get('time', 'Leave at') }}:</label>
    <input id="time" type="text" name="time" placeholder="hh:mm" value="{{ get('time', '') }}">
</p>
<p{{ !' class="error"' if errors.get('day') else '' }}>
    <label>{{ errors.get('day', 'Type of journey') }}:</label>
    <label class="n"><input type="radio" class="day_single" name="day" value="s"{{ ' checked' if get('day')=='s' else '' }}> Single</label>
    <label class="n"><input type="radio" class="day_ret" name="day" value="y"{{ ' checked' if get('day')=='y' else '' }}> Return same day</label>
    <label class="n"><input type="radio" class="day_ret" name="day" value="n"{{ ' checked' if get('day')=='n' else '' }}> Return</label>
</p>
<p id="time_ret_row"{{ !' class="error"' if errors.get('time_ret') else '' }}>
    <label for="time_ret">{{ errors.get('time_ret', 'Return at') }}: (optional)</label>
    <input id="time_ret" type="text" name="time_ret" placeholder="hh:mm" value="{{ get('time_ret', '') }}">
<br><small>(Providing a return time means I will take account of the time
restrictions and stations of the found return journey, for better or
worse.)</small> </p>
<p align="center">
    <input type="submit" value="Search">
</p>
</form>
<script>
$(function(){
    if (!$('.day_ret:checked').length) {
        $('#time_ret_row').hide();
    }
    $('.day_ret').click(function(){
        $('#time_ret_row').slideDown();
    });
    $('.day_single').click(function(){
        $('#time_ret_row').slideUp();
    });
    $('.ac').autocomplete({
        serviceUrl: '/ajax-station',
        beforeRender: function(c) {
            c.width('auto');
        },
        minChars: 2
    });
});
</script>
