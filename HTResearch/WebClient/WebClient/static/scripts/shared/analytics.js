/**
 * Provides a means of instantiating Google Analytics tracking. Instantiate this module on every page you'd like to
 * track.
 *
 * @module analytics
 */
define(function() {
    'use strict';

    return {
        startTracking: function() {
            (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

            //TODO: change this to 'atatlas.org' upon release
            ga('create', 'UA-48869339-1', 'unlhtprod.cloudapp.net');
            ga('send', 'pageview');
        }
    };
});