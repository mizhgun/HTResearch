/**
 * Demonstrates the Partner Map.
 */

require(['shared/analytics', 'datavis/partner-map', 'bootstrap'], function(Analytics, PartnerMap) {
    'use strict';

    Analytics.startTracking();
    PartnerMap.initialize('#partner-map', {width: 900, height: 600});
});
