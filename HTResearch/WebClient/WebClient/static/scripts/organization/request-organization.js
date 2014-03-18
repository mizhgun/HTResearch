require(['shared/analytics', 'shared/validators', 'jquery', 'bootstrap'], function(Analytics, Validators, $) {
    'use strict';

    $(function() {
        Analytics.startTracking();

        $('input[type="url"]').blur(function() {
             Validators.checkURL(this);
        });

        $('#request-org-nav').addClass("active");
    });
});

