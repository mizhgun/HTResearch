define(['jquery'], function($) {
    var SITE_URL = 'unlhtprod.cloudapp.net';

    function initialize() {
        var ele = document.getElementsByClassName('share');
          var ids = [];

          for (var i = 0; i < ele.length; i++) {
            ids.push(ele[i].id);
          }

          for (var i = 0; i < ele.length; i++){
            // Add href
            switch (ids[i]){
                case "facebook":
                    ele[i].href = 'http://www.facebook.com/sharer.php?s=100&p[title]=Anti-Human%20Trafficking%20Map&p[summary]=' +
                        'A%20map%20of%20anti-human%20trafficking%20efforts&p[url]=' + SITE_URL;
                    break;
                case "twitter":
                    ele[i].href = 'https://twitter.com/share';
                    break;
                case "gplus":
                    ele[i].href = 'https://plus.google.com/share?url=' + SITE_URL;
                    break;
                case "linkedin":
                    ele[i].href = 'http://www.linkedin.com/shareArticle?mini=true&url=' + SITE_URL + '&title=' +
                        'Anti-Human%20Trafficking%20Map';
                    break;
            }
          }

          // Set click event to open new window
          $(ele).click(function(event) {
            window.open(this.href, '_blank', 'status=1,height=570,width=520');
            return false;
          });
    }

    return { initialize: initialize };
});