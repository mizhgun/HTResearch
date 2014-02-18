define(['jquery',
        'jquery.tmpl',
        'async!https://maps.googleapis.com/maps/api/js?sensor=false&libraries=visualization',
        'goog!feeds,1'], function($) {
   'use strict';

    var NEWS_COUNT = 10;
    var NEWS_URL = 'https://news.google.com/news/feeds?output=rss&num=' + NEWS_COUNT + '&q=';
    var BASE_QUERY = 'prostitution OR "sex trafficking" OR "human trafficking" OR brothel OR "child trafficking" OR "anti trafficking"';
    var GENERAL_LOCATION = 'india';

    var NewsLoader = function() {
        this.newsFeed = null;
        this.geocoder = new google.maps.Geocoder();
    };

    NewsLoader.prototype = {
        /*updateNewsLocation: function(scope, center, bounds, orgData) {
            var self = this;
            this.moreNews = true;

            var loadNewsFromLocation = function (locationQuery) {
                var query = BASE_QUERY + ' ' + locationQuery;
                var feedParam = NEWS_URL + query.split(/,?\s/).join('+');
                self.newsFeed = new google.feeds.Feed(feedParam);
                self.newsCount = 0;
                self.loadMoreNews();
            };

            if (scope === 'general') {
                loadNewsFromLocation(GENERAL_LOCATION);
            } else if (scope === 'regional') {
                this.geocoder.geocode({
                    'latLng': center,
                    'bounds': bounds
                }, function (results, status) {
                    if (status === google.maps.GeocoderStatus.OK && results[0]) {
                        loadNewsFromLocation(results[0].formatted_address);
                    }
                });
            } else if (scope === 'organization') {
                if (orgData) {
                    loadNewsFromLocation(orgData.name);
                } else {
                    $('#news-results').html('<div class="no-results">Please select an organization.</div>');
                }
            }
        },*/
        loadNews: function(context) {
            var query = BASE_QUERY + (context ? (' ' + context) : '');
            var feedParam = NEWS_URL + query.split(/,?\s/).join('+');
            this.newsFeed = new google.feeds.Feed(feedParam);
            this.newsFeed.setNumEntries(NEWS_COUNT);
            this.newsFeed.load(function (result) {
                if (!result.error) {
                    var articles = result.feed.entries;
                    // Pull the relevant information out of each article
                    articles = $.map(articles, function(article) {
                        var result = {
                            title: $(article.content).find('td:last div:last a:first b:first').text(),
                            contentSnippet: $(article.content).find('td:last div:last font').eq(2).text(),
                            link: article.link
                        };
                        return result;
                    });

                    var newsCarousel = $('#news-carousel');
                    var newsDiv = $('#news-results');
                    newsDiv.find('.item').html('');

                    // Construct html from news articles
                    $.template('newsTemplate', $('#news-template').html());
                    _.each(articles, function(article, index) {
                        $.tmpl('newsTemplate', article).appendTo(newsDiv.find('.item').eq(index));
                    });
                    newsCarousel.carousel(0);

                    if ($(newsDiv).html()) {
                        $('.news-panel').show('slide', { direction: 'left' });
                    } else {
                        $('.news-panel').show('slide', { direction: 'left' });
                    }
                }
            });
        }
    };

    return NewsLoader;
});