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
                content: 'Give us a URL of any organization relating directly or indirectly to victims of human trafficking. We\'ll add this organization - and any related ones - to our records.'
            }
        );

        $('#request-org-nav').addClass("active");
    });
});

