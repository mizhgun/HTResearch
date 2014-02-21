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
                    ready(result.feed.entries);
                }
            });
        },
        // Load news into ticker
        loadNews: function(context, altText) {
            self.search(context, function(articles) {
                // See if there were any articles
                if (articles.length) {
                    // Pull the relevant information out of each article
                    articles = $.map(articles, function(article) {
                        var imageUrl = '';
                        var foundImage = $(article.content).find('img[src]');
                        if(foundImage.length) {
                            imageUrl = foundImage.attr('src');
                        }
                        return {
                            title: $(article.content).find('td:last div:last a:first b:first').text(),
                            date: article.publishedDate,
                            source: $(article.content).find('td:first a:first font').text().trim(),
                            contentSnippet: $(article.content).find('td:last div:last font').eq(2).text(),
                            link: article.link,
                            image: imageUrl
                        };
                    });

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
    };

    return NewsLoader;
});