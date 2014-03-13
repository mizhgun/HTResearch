require(['jquery'], function($) {
    $.get('/org-count/', function(data) {
        $('#org-count').text(data.count)
    });
    $.get('/contact-count/', function(data) {
        $('#contact-count').text(data.count);
    });
    $.get('/pub-count/', function(data) {
        $('#pub-count').text(data.count);
    });
});
