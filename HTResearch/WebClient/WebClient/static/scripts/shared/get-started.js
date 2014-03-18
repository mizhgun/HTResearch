require(['shared/analytics', 'jquery', 'bootstrap'], function(Analytics, $) {
    'use strict';

    $(function (){
        Analytics.startTracking();
        $('#get-started-nav').addClass('active');
    });
});