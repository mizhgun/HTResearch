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

        /**
         * Put items to search for here.
         * Properties are as follows:
         *     name: Name of the item searched for, should match data-search attribute for search results panels and
         *         filter control.
         *     url: URL of ajax call to get the data.
         *     search: Function to get the data, can be used instead of url.
         *         function(query, ready) { ... }
         *             where query is the search query, and
         *             ready is the function to which the results should be passed.
         *     toggleSelector: Search results panel toggle selector.
         *     collapseSelector: Collapsible region selector.
         *     listSelector: Search results list selector.
         *     linkClass: Class that will be on each link in search results.
         *     linkText: Function to determine what text will be displayed on links.
         *     onclick: Handler for clicking link.
         */
        var searchItems = [
            {
                name: 'organization',
                url: '/search-organizations/',
                toggleSelector: '#organization-toggle',
                collapseSelector: '#collapse-organizations',
                listSelector: '#organization-search-list',
                linkClass: 'org-link',
                linkText: function(item) { return item.name || item.organization_url || ''; },
                onclick: showOrganizationModal
            },
            {
                name: 'contact',
                url: '/search-contacts/',
                toggleSelector: '#contact-toggle',
                collapseSelector: '#collapse-contacts',
                listSelector: '#contact-search-list',
                linkClass: 'contact-link',
                linkText: function(item) { return (item.first_name || '') + ' ' + (item.last_name || '') },
                onclick: showContactModal
            },
            {
                name: 'publication',
                url: '/search-publications',
                toggleSelector: '#publication-toggle',
                collapseSelector: '#collapse-publications',
                listSelector: '#publication-search-list',
                linkClass: 'publication-link',
                linkText: function(item) { return item.title; },
                onclick: showPublicationModal
            },
            {
                name: 'news',
                search: newsLoader.search,
                toggleSelector: '#news-toggle',
                collapseSelector: '#collapse-news',
                listSelector: '#news-search-list',
                linkClass: 'news-link',
                linkText: function(item) { return item.title; },
                onclick: function(item) { window.open(item.link, '_blank'); }
            }
        ];

        // Update search when changing text input
        $('#search-box').bind("keyup change", _.debounce(function() {
            var searchText = $('#search-box').val().trim();

            SearchQuery.search(searchText, searchItems, map);
        }, 300));

        // Repeat search when setting items to visible
        $('#search-settings-dropdown :checkbox').change(function() {
            var searchItem = $(this).attr('data-search');
            var show = $(this).is(':checked');
            var resultsToShow = $('.panel[data-search=' + searchItem + ']');
            if(show) {
                var searchText = $('#search-box').val().trim();
                SearchQuery.search(searchText, searchItems, map, true);
            } else {
                resultsToShow.slideUp();
            }
        });

        // Prevent search form submit on enter
        $('#search-box').bind('keyup keypress', function (e) {
            var code = e.keyCode || e.which;
            if (code === 13) {
                e.preventDefault();
                return false;
            }
        });

        // Prevent clicks on search settings dropdown from closing the menu
        $('.dropdown-menu').on('click', function(e) {
            if($(this).hasClass('dropdown-menu-form')) {
                e.stopPropagation();
            }
        });

        // Legend
        var three_ps_legend = document.createElement('div');
        $(three_ps_legend).css('margin-bottom', '5px');
        $(three_ps_legend).html($("#map-legend").html());
        map.pushControl(google.maps.ControlPosition.LEFT_BOTTOM, three_ps_legend);

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
    function showOrganizationModal(org) {
        // Shows news based on the selected organization
        // Remove parentheses from organization name, get part of name before comma if necessary
        var alteredOrgName = org.name.replace(/ *\([^)]*\) */g, '');
        alteredOrgName = alteredOrgName.split(',')[0];
        var query = '"' + alteredOrgName + '"';
        newsLoader.loadNews(query, alteredOrgName);

        if (org.latlng && org.latlng.length > 0 && org.latlng[0] && org.latlng[1]) {
            map.showInfo(org);
        }
        else {
            map.closeAllInfowindows();

            Modal.createModal(org, '#bs-modal', '#bs-org-modal-template');
        }
    }

    function showContactModal(contact) {
        Modal.createModal(contact, '#bs-modal', '#contact-modal-template');
    }

    function showPublicationModal(pub) {
        Modal.createModal(pub, '#bs-modal', '#publication-modal-template');
    }

    return { initialize: initialize };
});