var searchResultsVisible = false;
var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var lastSearchedText;
var address;
var orgData = null, contactData = null, pubData = null;
var markers = [];
// for news loading
var maxNewsCount = 100;
var newsUrl = 'https://news.google.com/news/feeds?output=rss&num=' + maxNewsCount + '&q=';
var newsFeed = null;
var newsCount = 0;
var newsStepSize = 6;
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

    // Retrieve news whenever ready
    google.maps.event.addListener(map, 'idle', function () {
        var scope = $('input[name=news-scope]:checked').val();
        if (scope === 'regional') {
            updateNewsLocation(scope);
        }
    });

    // Make news scope switch work
    $('input[name=news-scope]').change(function (e) {
        $('#news-results').scrollTop(0);
        updateNewsLocation(e.target.value);
    });

    // Infinite scrolling for news
    $('#news-results').scroll(function () {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
            loadMoreNews();
        }
    });
    // Initially trigger infinite scrolling if there's not enough to fill

    // Legend
    var three_ps_legend = document.createElement('div');
    $(three_ps_legend).css('margin-bottom', '5px');
    $(three_ps_legend).html($("#map-legend").html());
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(three_ps_legend);
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
        loadMoreNews();
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

function loadMoreNews() {
    if (moreNews && newsFeed) {
        newsCount += newsStepSize;
        newsFeed.includeHistoricalEntries();
        newsFeed.setNumEntries(newsCount);
        newsFeed.load(function (result) {
            if (!result.error) {
                var articles = result.feed.entries;

                // See if there might be more news to load after this
                moreNews = (articles.length >= newsCount);

                newsCount = articles.length;

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
                    if (moreNews) {
                        $(newsDiv).append('<div class="news-footer ajax-loader"></div>');
                    } else {
                        $(newsDiv).append('<div class="news-footer"><i class="glyphicon glyphicon-stop"></i></div>');
                    }
                }
                var newsResultsDiv = $('#news-results');
                newsResultsDiv.html($(newsDiv).html());
                if (moreNews && newsResultsDiv.scrollTop() + newsResultsDiv.innerHeight() >= newsResultsDiv[0].scrollHeight) {
                    loadMoreNews();
                }
            }
        });
    }
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

function showSearchResults() {
    var searchText = $('#search-box').val().trim();
    if (lastSearchedText === searchText)
        return;
    lastSearchedText = searchText;
    var searchResultsDiv = $('#search-results-div');

    removeAllMarkers();
    if (searchText) {
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
            }
        ];

        // Perform each search
        _.each(searchItems, function(searchItem) {
            startAjaxSearch();
            $.ajax({
                type: 'GET',
                url: searchItem.url,
                data: {
                    'search_text': $('#search-box').val(),
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                dataType: 'html'
            }).done(function(data) {
                data = JSON.parse(data);
                $(searchItem.listSelector).html('');
                _.each(data.results, function(item) {
                    $('<a>' + searchItem.linkText(item) + '</a>')
                        .addClass(searchItem.linkClass)
                        .attr('href', 'javascript:void(0)')
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
            }).fail(function(data) {
                console.log(searchItem.name, 'search failed');
            }).always(function () {
                endAjaxSearch();
            });
        });

        if (!searchResultsVisible) {
            searchResultsDiv.toggle('slide', { direction: 'up' }, 500);

            searchResultsVisible = true;
        }
    } else {
        if (searchResultsVisible) {
            searchResultsDiv.toggle('slide', { direction: 'up' }, 500);

            searchResultsVisible = false;
        }
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
function showOrganizationModal() {
    orgData = $(this).data();

    // Search for news based on the selected organization
    var scope = $('input[name=news-scope]:checked').val();
    if (scope === 'organization') {
        updateNewsLocation(scope);
    }

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
    createBootstrapModal($modal, '#bs-contact-modal-template', contactData);
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
