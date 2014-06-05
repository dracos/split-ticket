<form action="/" method="get">

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
    <input type="submit" value="Search">
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
