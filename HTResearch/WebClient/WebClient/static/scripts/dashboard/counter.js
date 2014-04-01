require(['jquery'], function($) {
    $.get('/api/org-count/', function(data) {
        $('#org-count').text(data.count)
    });
    $.get('/api/contact-count/', function(data) {
        $('#contact-count').text(data.count);
    });
    $.get('/api/pub-count/', function(data) {
        $('#pub-count').text(data.count);
    });
});
