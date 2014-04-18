/**
 * Main script for the Organization Profile page.
 */

require(['shared/analytics', 'bootstrap'], function(Analytics) {
    'use strict';

    var editButton = $('#edit-btn');
    if (editButton) {
        editButton.tooltip({
            html: true,
            trigger: 'hover'
        });
    }

    Analytics.startTracking();
});