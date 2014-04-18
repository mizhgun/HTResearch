require(['shared/analytics', 'bootstrap'], function(Analytics) {
    var editButton = $('#edit-btn');
    if (editButton) {
        editButton.tooltip({
            html: true,
            trigger: 'hover'
        });
    }

    Analytics.startTracking();
});