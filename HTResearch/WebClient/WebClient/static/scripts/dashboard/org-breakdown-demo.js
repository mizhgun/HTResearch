require(['datavis/org-breakdown', 'bootstrap'], function(OrgBreakdown) {
    var options = {
        width: 300,
        height: 300,
        radius: 150
    };
    OrgBreakdown.initialize('#orgs-by-region', '#orgs-by-type', '#orgs-by-members', options);
});
