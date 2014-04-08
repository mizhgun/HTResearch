/**
 * Main script for the "About" page.
 */

require(['shared/analytics', 'jquery', 'bootstrap'], function(Analytics, $) {
    'use strict';

    Analytics.startTracking();
    $('#about-nav').addClass('active');
});