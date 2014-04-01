/**
 * Main script for the "About Us" page.
 */

require(['shared/analytics', 'jquery', 'bootstrap'], function(Analytics, $) {
    'use strict';

    $(function (){
        Analytics.startTracking();
        $('#about-us-nav').addClass('active');
    });
});