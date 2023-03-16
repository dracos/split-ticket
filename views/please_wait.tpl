% rebase('base.tpl', noindex=True)

% include('heading.tpl', new_journey=False)

<div class="results">

<p>I&rsquo;m just doing the calculations&hellip;
<span id="queue_size">
% if queue_size == 1:
(there is one other currently being processed)
% elif queue_size:
(there are {{ queue_size }} others currently being processed)
% end
</span>
</p>
<p><img src="/static/animated.gif" width=500 height=281 alt=""></p>
</div>

<script>
$(function(){
    function checkDone() {
        $.get('/ajax-job{{! url_job }}', function(data) {
            if (data.done) {
                window.location.reload();
                return;
            }
            if (data.queue_size == 1) {
                $('#queue_size').text( '(there is one other currently being processed)' );
            } else if (data.queue_size) {
                $('#queue_size').text( '(there are ' + data.queue_size + ' others currently being processed)' );
            } else {
                $('#queue_size').text( '' );
            }
            setTimeout(checkDone, data.refresh * 1000);
        });
    }
    setTimeout(checkDone, {{ refresh }} * 1000);
});
</script>
