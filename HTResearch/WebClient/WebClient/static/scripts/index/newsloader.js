define(['jquery',
        'jquery.tmpl',
        'async!https://maps.googleapis.com/maps/api/js?sensor=false&libraries=visualization',
        'goog!feeds,1'], function($) {
   'use strict';

    // Maximum number of news articles to retrieve
    var NEWS_COUNT = 10;
    // Url of news feed
    var NEWS_URL = 'https://news.google.com/news/feeds?output=rss&num=' + NEWS_COUNT + '&q=';
    // Base search terms for trafficking news
    var BASE_TERMS = [
        'prostitute',
        'prostitution',
        'sex trafficking',
        'human trafficking',
        'brothel',
        'child trafficking',
        'anti trafficking'
    ];
    // Base search query, based on base search terms
    var BASE_QUERY = BASE_TERMS.map(function(term) {
        if(term.indexOf(' ') >= 0) {
            return '"' + term + '"';
        } else {
            return term;
        }
    }).reduce(function(t1, t2) {
        return t1 + ' OR ' + t2;
    });
    // General location for news
    var GENERAL_LOCATION = 'India';

    var self;

    var NewsLoader = function() {
        this.newsFeed = null;
        this.lastContext = '';
        this.geocoder = new google.maps.Geocoder();

        // Find the original URL of a news article (not the Google Feed URL)
        this.cleanArticleUrl = function(rawUrl) {
            var cleanedUrl = '';
            rawUrl.split('?')[1].split('&').every(function(keyValueStr) {
                var keyValuePair = keyValueStr.split('=');
                if(keyValuePair[0] === 'url') {
                    cleanedUrl = keyValuePair[1];
                    return false;
                }
                return true;
            });
            return cleanedUrl || rawUrl;
        };

        // Test whether article is valid/relevant article by checking the title for relevant keywords
        this.isValidArticle = function(article) {
            return BASE_TERMS.some(function(keyword) {
                keyword = keyword.toLowerCase();
                return article.title.toLowerCase().indexOf(keyword) >= 0;
            });
        };

        // Extract relevant info from raw news results
        this.cleanNews = function(articles) {
            return $.map(articles, function(article) {
                // Find the image URL
                var imageUrl = '';
                var foundImage = $(article.content).find('img[src]');
                if(foundImage.length) {
                    imageUrl = foundImage.attr('src');
                }
                // Extract title, date, source, content, link, and image from the raw article
                return {
                    title: $(article.content).find('td:last div:last a:first b:first').text(),
                    date: article.publishedDate,
                    source: $(article.content).find('td:first a:first font').text().trim(),
                    contentSnippet: $(article.content).find('td:last div:last font').eq(2).text(),
                    link:  self.cleanArticleUrl(article.link),
                    image: imageUrl
                };
            });
        };
        self = this;
    };

    NewsLoader.prototype = {
        // Search for news
        search: function(searchQuery, ready) {
            var query = GENERAL_LOCATION + ' ' + BASE_QUERY + (searchQuery ? ' ' + searchQuery : '');
            var feedParam = NEWS_URL + query.split(/,?\s/).join('+');
            self.newsFeed = new google.feeds.Feed(feedParam);
            self.newsFeed.setNumEntries(10);
            self.newsFeed.load(function(result) {
                if (!result.error) {
                    var articles = result.feed.entries;
                    articles = self.cleanNews(articles);
                    articles = articles.filter(self.isValidArticle);
                    ready(articles);
                }
            });
        },
        // Load news into ticker by query
        loadNews: function(context, altText) {
            // Only reload when context changes
            if(context !== self.lastContext) {
                self.lastContext = context;
                self.search(context, function(articles) {
                    // See if there were any articles
                    if (articles.length) {
                        // Load articles into ticker
                        var newsCarousel = $('#news-carousel');
                        var newsDiv = $('#news-results');
                        newsDiv.find('.item').html('');

                        var carouselInner = newsCarousel.find('.carousel-inner');
                        var carouselIndicator = newsCarousel.find('.carousel-indicators');

                        carouselInner.find('.item').remove();
                        carouselIndicator.find('li').remove();

                        $.template('newsTemplate', $('#news-template').html());
                        _.each(articles, function(article, index) {
                            $.tmpl('newsTemplate', article)
                                .wrap('<div></div>')
                                .parent()
                                .addClass('item')
                                .appendTo(carouselInner);
                            $('<li></li>')
                                .attr('data-target', '#news-carousel')
                                .attr('data-slide-to', index)
                                .appendTo(carouselIndicator);
                        });

                        // Move to first article
                        carouselInner.find('.item').removeClass('active');
                        carouselInner.find('.item').eq(0).addClass('active');
                        carouselIndicator.find('li').removeClass('active');
                        carouselIndicator.find('li').eq(0).addClass('active');

                        // Show news panel and set context indicator
                        $('.news-panel').show('slide', { direction: 'right' });
                        $('#news-context').html(altText || context || GENERAL_LOCATION);

                        // Refresh panel to make sure carousel still works
                        $('#news-carousel').replaceWith($('#news-carousel')[0].outerHTML);
                        $('#news-carousel').carousel();
                    } else if(context) {
                        // If there were no results with context, try again for general results
                        self.loadNews();
                    } else {
                        // Hide news panel
                        $('.news-panel').hide('slide', { direction: 'right' });
                    }
                });
            }
        },
        // Load news into ticker by map region
        loadNewsByRegion: function(map) {
            self.geocoder.geocode({
                latLng: map.getCenter(),
                bounds: map.getBounds()
            }, function(results, status) {
                if(status == google.maps.GeocoderStatus.OK) {
                    var result = results[0];
                    if(result) {
                        var address = result.formatted_address;
                        var displayedAddress = address.split(',')[0];
                        // Format address for querying
                        var query = address.replace(/[0-9,]/g, '').split(/\s+/).join(' ');
                        self.loadNews(query, displayedAddress);
                    }
                }
            });
        }
    };

    return NewsLoader;
});