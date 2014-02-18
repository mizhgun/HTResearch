var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var lastSearchedText;
var address;
var orgData = null, contactData = null, pubData = null;
var markers = [];
// for news loading
var newsCount = 10;
var newsUrl = 'https://news.google.com/news/feeds?output=rss&num=' + newsCount + '&q=';
var newsFeed = null;
var baseQuery = 'prostitution OR "sex trafficking" OR "human trafficking" OR brothel OR "child trafficking" OR "anti trafficking"';
var generalLocation = 'india';
var geocoder = new google.maps.Geocoder();
var moreNews = true;

var MARKER_VALUES = {
    PREVENTION: 1 << 0,
    PROTECTION: 1 << 1,
    PROSECUTION: 1 << 2
};

// load Google Feeds API
google.load('feeds', '1');

function initialize() {
    var visited = getCookie("htresearchv2");
    if (!visited) {
        window.location = '/welcome';
    }

    var mapOptions = {
        center: initialLatLng,
        zoom: 5,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        mapTypeControlOptions: {
            position: google.maps.ControlPosition.TOP_LEFT
        },
        panControl: false,
        zoomControl: false,
        scaleControl: false,
        streetViewControl: false
    };

    map = new google.maps.Map($('#map-canvas')[0], mapOptions);

    $('#signup-btn').click(function (e) {
        $('#signup-div').easyModal({
            autoOpen: true,
            overlayOpacity: 0.3,
            overlayColor: "#333",
            overlayClose: false,
            closeButtonClass: ".btn-link"
        });

    });

    $('#login-btn').click(function (e) {
        $('#login-div').easyModal({
            autoOpen: true,
            overlayOpacity: 0.3,
            overlayColor: "#333",
            overlayClose: false,
            closeButtonClass: ".btn-link"
        });

    });

    // update search when changing text input
    $('#search-box').bind("keyup change", _.debounce(showSearchResults, 300));

    // prevent form submit on enter
    $('#search-box').bind('keyup keypress', function (e) {
        var code = e.keyCode || e.which;
        if (code === 13) {
            e.preventDefault();
            return false;
        }
    });

    // Search settings dropdown
    $('.dropdown-menu').on('click', function(e) {
        if($(this).hasClass('dropdown-menu-form')) {
            e.stopPropagation();
        }
    });

    $('#search-settings-dropdown :checkbox').change(function() {
        var searchItem = $(this).attr('data-search');
        var show = $(this).is(':checked');
        var resultsToShow = $('.panel[data-search=' + searchItem + ']');
        if(show) {
            showSearchResults(true);
        } else {
            resultsToShow.slideUp();
        }
    });

    // Retrieve news whenever ready
    google.maps.event.addListener(map, 'idle', function () {
        var scope = $('input[name=news-scope]:checked').val();
        if (scope === 'regional') {
            updateNewsLocation(scope);
        }
    });

    // Legend
    var three_ps_legend = document.createElement('div');
    $(three_ps_legend).css('margin-bottom', '5px');
    $(three_ps_legend).html($("#map-legend").html());
    map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(three_ps_legend);

    // Load news
    loadNews();
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

function updateNewsLocation(scope) {
    moreNews = true;
    var loadNewsFromLocation = function (locationQuery) {
        var query = baseQuery + ' ' + locationQuery;
        var feedParam = newsUrl + query.split(/,?\s/).join('+');
        newsFeed = new google.feeds.Feed(feedParam);
        newsCount = 0;
        loadNews();
    };

    if (scope === 'general') {
        loadNewsFromLocation(generalLocation);
    } else if (scope === 'regional') {
        geocoder.geocode({
            'latLng': map.getCenter(),
            'bounds': map.getBounds()
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
}

function loadNews(context) {
    var query = baseQuery + (context ? (' ' + context) : '');
    var feedParam = newsUrl + query.split(/,?\s/).join('+');
    newsFeed = new google.feeds.Feed(feedParam);
    newsFeed.setNumEntries(newsCount);
    newsFeed.load(function(result) {
        if (!result.error) {
            var articles = result.feed.entries;
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
                $('.news-panel').show("slide", { direction: "left" });
            } else {
                $('.news-panel').show("slide", { direction: "left" });
            }
        }
    });
}

function plotMarker(data) {
    if (data.latlng && data.latlng.length > 0 && data.latlng[0] && data.latlng[1]) {
        var coord = new google.maps.LatLng(data.latlng[0], data.latlng[1]);

        var marker_url = "";
        var is_prev = $.inArray(5, data.types) > -1; // Value for prevention enum
        var is_prot = $.inArray(6, data.types) > -1; // Value for protection enum
        var is_pros = $.inArray(7, data.types) > -1; // Value for prosecution enum
        var marker_switch = 0;
        if (is_prev)
            marker_switch |= MARKER_VALUES.PREVENTION;
        if (is_prot)
            marker_switch |= MARKER_VALUES.PROTECTION;
        if (is_pros)
            marker_switch |= MARKER_VALUES.PROSECUTION;
        switch (marker_switch) {
            case MARKER_VALUES.PREVENTION: //Prevention only
                marker_url = "/static/images/prevention_pin_small.png"
                break;
            case MARKER_VALUES.PROTECTION: //Protection only
                marker_url = "/static/images/protection_pin_small.png"
                break;
            case (MARKER_VALUES.PREVENTION | MARKER_VALUES.PROTECTION): //Prevention and Protection
                marker_url = "/static/images/prot_prev_pin_small.png"
                break;
            case MARKER_VALUES.PROSECUTION: //Prosecution only
                marker_url = "/static/images/prosecution_pin_small.png"
                break;
            case (MARKER_VALUES.PREVENTION | MARKER_VALUES.PROSECUTION): //Prevention and Prosecution
                marker_url = "/static/images/prev_pros_pin_small.png"
                break;
            case (MARKER_VALUES.PROTECTION | MARKER_VALUES.PROSECUTION): //Protection and Prosecution
                marker_url = "/static/images/prot_pros_pin_small.png"
                break;
            case (MARKER_VALUES.PREVENTION | MARKER_VALUES.PROTECTION | MARKER_VALUES.PROSECUTION): //All
                marker_url = "/static/images/all_pin_small.png"
                break;
            default: // keep default
                marker_url = "/static/images/default_pin_small.png";
                break;
        }

        var new_marker = new google.maps.Marker({
            map: map,
            position: coord,
            icon: {
                url: marker_url,
                size: new google.maps.Size(39, 32),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(9, 32)
            }
        });

        data.img_path = "/static/images/office_building_icon.png";
        var html = $("#modal-template").tmpl(data);

        var new_infowindow = new google.maps.InfoWindow({
            content: html.html()
        });

        $(document).bind("mousedown", function(e){
            //TODO: Find a not janky way - Marcus
            $('#map-modal').parents().eq(2).attr('id', 'map-modal-parent');
            if((!$(e.target).parents('#map-modal-parent').size() || e.target.id == "map-modal-parent")) {
                closeAllInfowindows();
            }
        });

        google.maps.event.addListener(new_marker, 'click', function () {
            var thisMarker = findMarker(new_marker);
            if (!thisMarker) {
                new_infowindow.open(map, new_marker);
                closeAllInfowindows();
            } else if (thisMarker.open) {
                closeAllInfowindows();
                thisMarker.infowindow.close();
                thisMarker.open = false;
            } else {
                closeAllInfowindows();
                thisMarker.infowindow.open(map, new_marker);
                thisMarker.open = true;
            }
        });

        markers.push({
            id: data.id,
            marker: new_marker,
            infowindow: new_infowindow,
            open: false
        });
    }
}

function removeAllMarkers() {
    $.each(markers, function (index, value) {
        value.marker.setMap(null);
    });
    markers = [];
}

function closeAllInfowindows() {
    $.each(markers, function (index, value) {
        value.infowindow.close();
        value.open = false;
    });
}

function findMarker(marker) {
    var retMarker;
    for (var i = 0; i < markers.length; i++) {
        if (marker === markers[i].marker) {
            retMarker = markers[i];
            break;
        }
    }
    return retMarker;
}

function findMarkerById(id) {
    var marker;
    for (var i = 0; i < markers.length; i++) {
        if (id === markers[i].id) {
            marker = markers[i];
            break;
        }
    }
    return marker;
}

function showSearchResults(reload) {
    var searchText = $('#search-box').val().trim();
    if (!reload && lastSearchedText === searchText)
        return;
    lastSearchedText = searchText;
    var searchResultsDiv = $('#search-results-div');

    removeAllMarkers();
    if (searchText) {
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
                search: function(searchQuery, ready) {
                    query = baseQuery + ' ' + searchQuery;
                    var feedParam = newsUrl + query.split(/,?\s/).join('+');
                    newsFeed = new google.feeds.Feed(feedParam);
                    newsFeed.setNumEntries(10);
                    newsFeed.load(function(result) {
                        if (!result.error) {
                            ready(result.feed.entries);
                        }
                    });
                },
                toggleSelector: '#news-toggle',
                collapseSelector: '#collapse-news',
                listSelector: '#news-search-list',
                linkClass: 'news-link',
                linkText: function(item) { return item.title; },
                onclick: function(item) { window.open(item.link, '_blank'); }
            }
        ];

        // Default ajax search function
        var ajaxSearch = function(searchQuery, ready, searchItem) {
            // Do an ajax call with the given url
            $.ajax({
                type: 'GET',
                url: searchItem.url,
                data: {
                    'search_text': searchQuery,
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                dataType: 'html'
            }).done(function(data) {
<<<<<<< HEAD
                var results = JSON.parse(data).results;
                ready(results);
=======
                data = JSON.parse(data);
                $(searchItem.listSelector).html('');
                // Show number of results
                var resultCount = data.results.length;
                var resultsString = (resultCount >= 10 ? '10+' : resultCount) + ' results';
                $(searchItem.toggleSelector).parent().next('.count').text(resultsString);
                // Hide or show panel based on availability of results
                if(resultCount) {
                    // Show panel
                    $(searchItem.toggleSelector).closest('.panel').show();
                    // Display results
                    _.each(data.results, function(item) {
                        $('<a>' + searchItem.linkText(item) + '</a>')
                            .addClass(searchItem.linkClass)
                            .attr('href', 'javascript:void(0)')
                            .attr('title', searchItem.linkText(item))
                            .data(item)
                            .wrap('<li></li>')
                            .parent()
                            .appendTo(searchItem.listSelector);
                    });
                    if (data) {
                        $(searchItem.toggleSelector).closest('.panel').show();
                        $(searchItem.toggleSelector).attr('data-toggle', 'collapse');
                        $(searchItem.toggleSelector).removeClass('disabled');
                        $(searchItem.collapseSelector).collapse('show');
                    } else {
                        $(searchItem.toggleSelector).closest('.panel').hide();
                    }
                    $(searchItem.toggleSelector).click(function (e) {
                        e.preventDefault();
                    });
                    $('.modal').modal({ show: false });
                    $('.' + searchItem.linkClass)
                        .click(searchItem.onclick)
                        .each(function (index, value) {
                            plotMarker($(value).data());
                        });
                } else {
                    // Hide panel
                    $(searchItem.toggleSelector).closest('.panel').hide();
                }
>>>>>>> R5_NationalTreasure
            }).fail(function(data) {
                console.log(searchItem.name, 'search failed');
                ready([]);
            });
        }

        // Perform each search
        _.each(searchItems, function(searchItem) {
            // See if we want to search for this item
            var shouldSearch = $(':checkbox:checked[data-search=' + searchItem.name + ']').length > 0;
            if(shouldSearch) {
                var searchQuery = $('#search-box').val();
                // Search begin
                startAjaxSearch();
                // See if we should do a custom search or just an ajax call
                var search = searchItem.search || ajaxSearch;
                // Retrieve search results
                search(searchQuery, function(results) {
                    // Show search results for this item
                    displaySearchResults(searchItem, results);
                    // Search end
                    endAjaxSearch();
                }, searchItem);
            } else {
                // Hide panel
                $(searchItem.toggleSelector).closest('.panel').hide();
            }
        });

        searchResultsDiv.slideDown();
    } else {
        searchResultsDiv.slideUp();
    }
}

function displaySearchResults(searchItem, results) {
    // Clear previous results
    $(searchItem.listSelector).html('');
    // Show number of results
    var resultCount = results.length;
    var resultsString = (resultCount >= 10 ? '10+' : resultCount)
        + ' result'
        + (resultCount == 1 ? '' : 's');
    $(searchItem.toggleSelector).find('.count').text(resultsString);
    // Hide or show panel based on availability of results
    if(resultCount) {
        // Show panel
        $(searchItem.toggleSelector).closest('.panel').show();
        // Display results
        _.each(results, function(item) {
            $('<a>' + searchItem.linkText(item) + '</a>')
                .addClass(searchItem.linkClass)
                .attr('href', 'javascript:void(0)')
                .click(function() {
                    if(searchItem.onclick) {
                        searchItem.onclick(item);
                    }
                })
                .data(item)
                .wrap('<li></li>')
                .parent()
                .appendTo(searchItem.listSelector);

            plotMarker(item);
        });
        if (results.length) {
            $(searchItem.toggleSelector).closest('.panel').show();
            $(searchItem.toggleSelector).attr('data-toggle', 'collapse');
            $(searchItem.toggleSelector).removeClass('disabled');
            $(searchItem.collapseSelector).collapse('show');
        } else {
            $(searchItem.toggleSelector).closest('.panel').hide();
        }
        $(searchItem.toggleSelector).click(function (e) {
            e.preventDefault();
        });
        $('.modal').modal({ show: false });
    } else {
        // Hide panel
        $(searchItem.toggleSelector).closest('.panel').hide();
    }
}

var searchesPending = 0;
function startAjaxSearch() {
    searchesPending++;
    if (searchesPending === 1) {
        $('#search-ajax-loader').removeClass('hidden');
    }
}
function endAjaxSearch() {
    searchesPending--;
    if (searchesPending === 0) {
        $('#search-ajax-loader').addClass('hidden');
    }
}

// Show modals
function showOrganizationModal(link) {
    orgData = link;

    // Shows news based on the selected organization
    loadNews(orgData.name + ' ' + orgData.keywords);

    if (orgData.latlng && orgData.latlng.length > 0) {
        // Get the lat, long values of the address
        searchedLatLng = new google.maps.LatLng(orgData.latlng[0], orgData.latlng[1]);
        plotOrganization(orgData);
    }
    else {
        closeAllInfowindows();

        var $modal = $('.modal').modal();
        createBootstrapModal($modal, '#bs-org-modal-template', orgData);
    }
}

function showContactModal() {
    contactData = $(this).data();
    var $modal = $('.modal').modal({
        show: false
    });
    createBootstrapModal($modal, '#contact-modal-template', contactData);
}

function showPublicationModal(){
    pubData = $(this).data();
    var $modal = $('.modal').modal({
        show: false
    })
    createBootstrapModal($modal, '#publication-modal-template', pubData)
}

// Show organization location on map
function plotOrganization(data) {
    if (data.latlng && data.latlng.length > 0 && data.latlng[0] && data.latlng[1]) {
        var coord = new google.maps.LatLng(data.latlng[0], data.latlng[1]);
        map.setCenter(coord);

        closeAllInfowindows();

        var marker = findMarkerById(data.id);

        marker.infowindow.open(map, marker.marker);
        marker.open = true;
    } else {
        var $modal = $('.modal').modal();
        createBootstrapModal($modal, '#bs-org-modal-template', data);
    }
}

function createBootstrapModal(m, modal_template, data) {
    // Do a bootstrap modal
    var html = $(modal_template).tmpl(data);

    $('#bs-modal').html(html);

    m.modal('show');
}

$(function () {
    initialize();
});
