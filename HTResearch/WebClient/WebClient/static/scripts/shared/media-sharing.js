/**
 * Provides a means of initializing the social media sharing elements.
 *
 * @module media-sharing
 */
define(['jquery', 'underscore'], function($, _) {
    'use strict';

    var SITE_URL = 'http://unlhtprod.cloudapp.net';

    /**
     * Initializes the DOM elements for Facebook, Twitter, Google+, and LinkedIn sharing.
     */
    function initialize() {
        var elements = $('.share');
        var height, width;

        //Iterate over each given social medium and initialize them with sizes and urls
        _.each(elements, function(ele){
            // Add href
            switch (ele.id){
                case "facebook":
                    ele.href = 'http://www.facebook.com/sharer.php?s=100&p[title]=Anti-Human%20Trafficking%20Map&p[summary]=' +
                        'A%20map%20of%20anti-human%20trafficking%20efforts&p[url]=' + SITE_URL;
                    height = 450;
                    width = 420;
                    break;
                case "twitter":
                    ele.href = 'https://twitter.com/intent/tweet?url=' + SITE_URL;
                    height = 550;
                    width = 420;
                    break;
                case "gplus":
                    ele.href = 'https://plus.google.com/share?url=' + SITE_URL;
                    height = 500;
                    width = 450;
                    break;
                case "linkedin":
                    ele.href = 'http://www.linkedin.com/shareArticle?mini=true&url=' + SITE_URL + '&title=' +
                        'Anti-Human%20Trafficking%20Map';
                    height = 450;
                    width = 450;
                    break;
            }
        });

        // Set click event to open new window
        elements.click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.open(this.href, '_blank', 'status=1,height=' + height + ',width=' + width);
        });
    }

    return { initialize: initialize };
});