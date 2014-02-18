define(['index/modal',
        'index/map',
        'index/newsloader',
        'index/heatmap',
        'index/searchquery',
        'underscore',
        'jquery',
        'jquery.tmpl',
        'bootstrap',
        'async!https://maps.googleapis.com/maps/api/js?sensor=false&libraries=visualization'],
    function(Modal, Map, NewsLoader, HeatMap, SearchQuery, _, $) {
    'use strict';

    var map;
    var orgData;
    var newsLoader;

    function initialize() {
        var visited = getCookie("htresearchv2");
        if (!visited) {
            window.location = '/welcome';
        }

        map = new Map($('#map-canvas')[0]);
        newsLoader = new NewsLoader();
        HeatMap.initialize(map.getMap());

        // update search when changing text input
        $('#search-box').bind("keyup change", _.debounce(function() {
            var searchText = $('#search-box').val().trim();

            // Put items to search for here.
            var searchItems = [
                {
                    name: 'Organization',
                    url: '/search-organizations/',
                    toggleSelector: '#organization-toggle',
                    collapseSelector: '#collapse-organizations',
                    listSelector: '#organization-search-list',
                    linkClass: 'org-link',
                    linkText: function(item) { return item.name || item.organization_url || ''; },
                    onclick: showOrganizationModal
                },
                {
                    name: 'Contact',
                    url: '/search-contacts/',
                    toggleSelector: '#contact-toggle',
                    collapseSelector: '#collapse-contacts',
                    listSelector: '#contact-search-list',
                    linkClass: 'contact-link',
                    linkText: function(item) { return (item.first_name || '') + ' ' + (item.last_name || '') },
                    onclick: showContactModal
                },
                {
                    name: 'Publication',
                    url: '/search-publications',
                    toggleSelector: '#publication-toggle',
                    collapseSelector: '#collapse-publications',
                    listSelector: '#publication-search-list',
                    linkClass: 'publication-link',
                    linkText: function(item) { return item.title; },
                    onclick: showPublicationModal
                }
            ];

            SearchQuery.showResults(searchText, searchItems, map);
        }, 300));

        // prevent form submit on enter
        $('#search-box').bind('keyup keypress', function (e) {
            var code = e.keyCode || e.which;
            if (code === 13) {
                e.preventDefault();
                return false;
            }
        });

        // Retrieve news whenever ready
        map.bind('idle', function () {
            var scope = $('input[name=news-scope]:checked').val();
            if (scope === 'regional') {
                newsLoader.updateNewsLocation(scope, map.getMap().getCenter(), map.getMap().getBounds(), orgData);
            }
        });

        // Make news scope switch work
        $('input[name=news-scope]').change(function (e) {
            $('#news-results').scrollTop(0);
            newsLoader.updateNewsLocation(e.target.value, map.getMap().getCenter(), map.getMap().getBounds(), orgData);
        });

        // Infinite scrolling for news
        $('#news-results').scroll(function () {
            if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
                newsLoader.loadMoreNews();
            }
        });
        // Initially trigger infinite scrolling if there's not enough to fill

        // Legend
        var three_ps_legend = document.createElement('div');
        $(three_ps_legend).css('margin-bottom', '5px');
        $(three_ps_legend).html($("#map-legend").html());
        map.pushControl(google.maps.ControlPosition.RIGHT_BOTTOM, three_ps_legend);

        // Load news
        newsLoader.loadNews();
    }

    function getCookie(name) {
        var arg = name + "=";
        var argLength = arg.length;
        var cookieLength = document.cookie.length;
        var i = 0;
        while (i < cookieLength) {
            var j = i + argLength;
            if (document.cookie.substring(i, j) === arg)
                return "here";
            i = document.cookie.indexOf(" ", i) + 1;
            if (i === 0) break;
        }
        return null;
    }

    // Show modals
    function showOrganizationModal() {
        orgData = $(this).data();

        // Shows news based on the selected organization
        newsLoader.loadNews(orgData.name + ' ' + orgData.keywords);

        if (orgData.latlng && orgData.latlng.length > 0 && orgData.latlng[0] && orgData.latlng[1]) {
            map.showInfo(orgData);
        }
        else {
            map.closeAllInfowindows();

            Modal.createModal(orgData, '#bs-modal', '#bs-org-modal-template');
        }
    }

    function showContactModal() {
        var data = $(this).data();

        Modal.createModal(data, '#bs-modal', '#contact-modal-template');
    }

    function showPublicationModal(){
        var data = $(this).data();

        Modal.createModal(data, '#bs-modal', '#publication-modal-template');
    }


    return { initialize: initialize };
});