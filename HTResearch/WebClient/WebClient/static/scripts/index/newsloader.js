define(['jquery',
        'jquery.tmpl',
        'async!https://maps.googleapis.com/maps/api/js?sensor=false&libraries=visualization',
        'goog!feeds,1'], function($) {
   'use strict';

    var MAX_NEWS_COUNT = 100;
    var NEWS_URL = 'https://news.google.com/news/feeds?output=rss&num=' + MAX_NEWS_COUNT + '&q=';
    var BASE_QUERY = 'prostitution OR "sex trafficking" OR "human trafficking" OR brothel OR "child trafficking" OR "anti trafficking"';
    var GENERAL_LOCATION = 'india';

    var NewsLoader = function() {
        this.newsCount = 0;
        this.newsStepSize = 6;
        this.moreNews = true;
        this.newsFeed = null;
        this.geocoder = new google.maps.Geocoder();
    };

    NewsLoader.prototype = {
        updateNewsLocation: function(scope, center, bounds, orgData) {
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
        },
        loadMoreNews: function() {
            if (this.moreNews && this.newsFeed) {
                this.newsCount += this.newsStepSize;
                this.newsFeed.includeHistoricalEntries();
                this.newsFeed.setNumEntries(this.newsCount);
                this.newsFeed.load(function (result) {
                    if (!result.error) {
                        var articles = result.feed.entries;

                        // See if there might be more news to load after this
                        this.moreNews = (articles.length >= this.newsCount);

                        this.newsCount = articles.length;

                        // Construct html from news articles
                        $.template('newsTemplate', $('#news-template').html());
                        var newsDiv = $('<div></div>');
                        $.each(articles, function (index) {
                            var newsArticle = $.tmpl('newsTemplate', this);
                            // Do some HTML processing to make the articles look better
                            $(newsArticle).find('tr').each(function () {
                                $(this).find('td:last').prepend($(this).find('td:first').html());
                            });
                            $(newsArticle).find('br, '
                                + 'tr td:first, '
                                + 'tr td:last div:first').remove();
                            $(newsArticle).find('*').css('padding', '0');
                            $(newsArticle).find('a').attr('target', '_blank');
                            $(newsArticle).find('a, font').css({'display': 'block', 'margin-right': '5px'});
                            $(newsArticle).find('a:has(img)').css({
                                'width': '80px',
                                'float': (index % 2 === 0) ? 'left' : 'right',
                                'text-align': 'center'
                            });
                            $(newsArticle).find('img').css({
                                'width': '80px',
                                'height': '80px',
                                'border-radius': '5px'
                            });
                            $(newsArticle).find('td div a:first').css('font-size', '14px');
                            $(newsDiv).append(newsArticle);
                        });
                        if (!$(newsDiv).html()) {
                            $(newsDiv).append('<div class="no-results">No results found.</div>');
                        } else {
                            if (this.moreNews) {
                                $(newsDiv).append('<div class="news-footer ajax-loader"></div>');
                            } else {
                                $(newsDiv).append('<div class="news-footer"><i class="glyphicon glyphicon-stop"></i></div>');
                            }
                        }
                        var newsResultsDiv = $('#news-results');
                        newsResultsDiv.html($(newsDiv).html());
                        if (this.moreNews && newsResultsDiv.scrollTop() + newsResultsDiv.innerHeight() >= newsResultsDiv[0].scrollHeight) {
                            this.loadMoreNews();
                        }
                    }
                });
            }
        }
    };

    return NewsLoader;
});