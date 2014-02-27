define(['jquery',
        'jquery.tmpl',
        'async!https://maps.googleapis.com/maps/api/js?sensor=false&libraries=visualization',
        'goog!feeds,1'], function($) {
   'use strict';

    var NEWS_COUNT = 10;
    var NEWS_URL = 'https://news.google.com/news/feeds?output=rss&num=' + NEWS_COUNT + '&q=';
    var BASE_QUERY = 'prostitution OR "sex trafficking" OR "human trafficking" OR brothel OR "child trafficking" OR "anti trafficking"';
    var GENERAL_LOCATION = 'India';

    var self;

    var NewsLoader = function() {
        this.newsFeed = null;
        this.lastContext = '';
        this.geocoder = new google.maps.Geocoder();
        // Clean raw news resutls, i.e. filter out irrelevant sites and extract the important info
        this.cleanNews = function(articles) {
            // TODO: List of domains that we don't want news from
            var blockedDomains = [

            ];

            // Pull the relevant information out of each article
            articles = $.map(articles, function(article) {
                // Find the image URL
                var imageUrl = '';
                var foundImage = $(article.content).find('img[src]');
                if(foundImage.length) {
                    imageUrl = foundImage.attr('src');
                }
                // Find the original URL of the news article (not the Google Feed URL)
                var rawUrl = article.link;
                var cleanedUrl = '';
                rawUrl.split('?')[1].split('&').every(function(keyValueStr) {
                    var keyValuePair = keyValueStr.split('=');
                    if(keyValuePair[0] === 'url') {
                        cleanedUrl = keyValuePair[1];
                        return false;
                    }
                    return true;
                });
                cleanedUrl = cleanedUrl || rawUrl;
                // Extract title, date, source, content, link, and image from the raw article
                return {
                    title: $(article.content).find('td:last div:last a:first b:first').text(),
                    date: article.publishedDate,
                    source: $(article.content).find('td:first a:first font').text().trim(),
                    contentSnippet: $(article.content).find('td:last div:last font').eq(2).text(),
                    link: cleanedUrl,
                    image: imageUrl
                };
            });

            // Remove articles from blocked domains
            articles = articles.filter(function(article) {
                var domain = article.link.split('//')[1].split('/')[0].replace(/^www\./, '');
                return $.inArray(domain, blockedDomains) < 0;
            });

            return articles;
        }
        self = this;
    };

    NewsLoader.prototype = {
        loading: false,
        // Search for news
        search: function(searchQuery, ready) {
            if(!self.loading) {
                var query = GENERAL_LOCATION + ' ' + BASE_QUERY + (searchQuery ? ' ' + searchQuery : '');
                var feedParam = NEWS_URL + query.split(/,?\s/).join('+');
                self.newsFeed = new google.feeds.Feed(feedParam);
                self.newsFeed.setNumEntries(10);
                self.loading = true;
                self.newsFeed.load(function(result) {
                    if (!result.error) {
                        ready(result.feed.entries);
                    }
                    self.loading = false;
                });
            }
        },
        // Load news into ticker by query
        loadNews: function(context, altText) {
            // Only reload when context changes
            if(context !== self.lastContext) {
                self.lastContext = context;
                self.search(context, function(articles) {
                    // See if there were any articles
                    articles = self.cleanNews(articles);
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