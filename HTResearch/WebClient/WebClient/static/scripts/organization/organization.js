/**
 * Main script for the Organization Profile page.
 */

require(['shared/analytics', 'organization/word-cloud', 'bootstrap'], function(Analytics, WordCloud) {
    'use strict';

    Analytics.startTracking();
    WordCloud.initialize();
});