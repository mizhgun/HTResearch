define(['jquery', 'underscore'], function($, _) {
    var SITE_URL = 'unlhtprod.cloudapp.net';

    function initialize() {
        var elements = $('.share');

        _.each(elements, function(ele){
            // Add href
            switch (ele.id){
                case "facebook":
                    ele.href = 'http://www.facebook.com/sharer.php?s=100&p[title]=Anti-Human%20Trafficking%20Map&p[summary]=' +
                        'A%20map%20of%20anti-human%20trafficking%20efforts&p[url]=' + SITE_URL;
                    break;
                case "twitter":
                    ele.href = 'https://twitter.com/share';
                    break;
                case "gplus":
                    ele.href = 'https://plus.google.com/share?url=' + SITE_URL;
                    break;
                case "linkedin":
                    ele.href = 'http://www.linkedin.com/shareArticle?mini=true&url=' + SITE_URL + '&title=' +
                        'Anti-Human%20Trafficking%20Map';
                    break;
            }


        });

        // Set click event to open new window
        elements.click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.open(this.href, '_blank', 'status=1,height=570,width=520');
        });
    }

    return { initialize: initialize };
});