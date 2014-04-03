/**
 * Performs validation on a requested organization url.
 */

require(['shared/analytics', 'shared/validators', 'jquery', 'bootstrap'], function(Analytics, Validators, $) {
    'use strict';

    $(function() {
        Analytics.startTracking();

        $('input[type="url"]').blur(function() {
             Validators.checkURL(this);
        });

        $('#help-text').popover(
            {
                trigger: 'hover',
                placement: 'right',
                html: 'true'
            }
        );

        $('#request-org-nav').addClass("active");
    });
});

