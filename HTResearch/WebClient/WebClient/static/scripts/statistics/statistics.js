require(['jquery', 'shared/analytics', 'datavis/partner-map', 'datavis/org-breakdown', 'bootstrap'],
    function($, Analytics, PartnerMap, OrgBreakdown) {
    'use strict';

    $.get('/api/org-count/', function(data) {
        $('#org-count').text(data.count)
    });
    $.get('/api/contact-count/', function(data) {
        $('#contact-count').text(data.count);
    });
    $.get('/api/pub-count/', function(data) {
        $('#pub-count').text(data.count);
    });

    var options = {
        width: 350,
        height: 350,
        radius: 150
    };
    OrgBreakdown.initialize('#orgs-by-region', '#orgs-by-type', '#orgs-by-members', options);

    Analytics.startTracking();
    PartnerMap.initialize('#partner-map', {height: 600});
});
