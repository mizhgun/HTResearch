var searchResultsVisible = false;
var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var address;
var orgData, contactData, pubData;
var infowindow = null;
var marker = null;
// for news loading
var maxNewsCount = 100;
var newsUrl = 'https://news.google.com/news/feeds?output=rss&num=' + maxNewsCount + '&q=';
var newsFeed = null;
var newsCount = 0;
var newsStepSize = 6;

// load Google Feeds API
google.load('feeds', '1');

function initialize() {
	var mapOptions = {
	  center: initialLatLng,
	  zoom: 5,
	  mapTypeId: google.maps.MapTypeId.ROADMAP,
	  panControl: false,
	  zoomControl: false,
	  scaleControl: false
	};
        
	//Didn't accept a jquery selector
	map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

	$('#signup-btn').click(function(e) {
		$('#signup-div').easyModal({
			autoOpen: true,
			overlayOpacity: 0.3,
			overlayColor: "#333",
			overlayClose: false,
			closeButtonClass: ".btn-link"
		});

	});

	$('#login-btn').click(function(e) {
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
    $('#search-box').bind('keyup keypress', function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            e.preventDefault();
            return false;
        }
    });

	$('a.org-link').click(function(e){
        geocoder.geocode({'latLng': searchedLatLng, 'address': address}, plotOrganization);
    });

    //This function is in welcome.js
    google.maps.event.addListenerOnce(map, 'idle', initiateTutorial);

    // Retrieve news
    setNewsQuery('human trafficking india');
    loadNews();
    // Infinite scrolling for news
    $('#news-results').scroll(function() {
        if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
            loadNews();
        }
    });
}

function setNewsQuery(query) {
    newsFeed = newsFeed || new google.feeds.Feed(newsUrl + query.split().join('+'));
    newsCount = 0;
}

function loadNews() {
    newsCount += newsStepSize;
    newsFeed.includeHistoricalEntries();
    newsFeed.setNumEntries(newsCount);
    newsFeed.load(function(result) {
        if(!result.error) {
            var articles = result.feed.entries;
            newsCount = articles.length;
            $.template('newsTemplate', $('#news-template').html());
            var newsDiv = $('<div></div>');
            $.each(articles, function(index) {
                var newsArticle = $.tmpl('newsTemplate', this);
                // Do some HTML processing to make the articles look better
                $(newsArticle).find('tr').each(function() {
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
                    'float': (index % 2 == 0) ? 'left' : 'right',
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
            $('#news-results').html($(newsDiv).html());
        }
    });
}

function showSearchResults() {
    var searchText = $('#search-box').val().trim();
    var searchResultsDiv = $('#search-results-div');

    if(searchText) {
        // Put items to search for here.
        var searchItems = [
            {
                name: 'Organization',
                url: '/search_organizations/',
                toggleSelector: '#organization-toggle',
                collapseSelector: '#collapse-organizations',
                listSelector: '#organization-search-list',
                linkSelector: '.org-link',
                linkCallback: showOrganizationModal
            },
            {
                name: 'Contact',
                url: '/search_contacts/',
                toggleSelector: '#contact-toggle',
                collapseSelector: '#collapse-contacts',
                listSelector: '#contact-search-list',
                linkSelector: '.contact-link',
                linkCallback: showContactModal
            }
        ];

        // Perform each search
        _.each(searchItems, function(item) {
            startAjaxSearch();
            $.ajax({
                type: 'GET',
                url: item.url,
                data: {
                    'search_text': $('#search-box').val(),
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                dataType: 'html'
            }).done(function(data) {
                data = data.trim();
                if (data) {
                    $(item.toggleSelector).attr('data-toggle', 'collapse');
                    $(item.toggleSelector).removeClass('disabled');
                    $(item.collapseSelector).collapse('show');
                } else {
                    $(item.toggleSelector).attr('data-toggle', '');
                    $(item.toggleSelector).addClass('disabled');
                    $(item.collapseSelector).collapse('hide');
                }
                $(item.toggleSelector).click(function(e) {
                    e.preventDefault();
                });
                $(item.listSelector).html(data);
                $('.modal').modal({ show: false });
                $(item.linkSelector).click(item.linkCallback);
            }).fail(function() {
                console.log(item.name, 'search failed');
            }).always(function() {
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
    if (searchesPending == 1) {
        $('#search-ajax-loader').removeClass('hidden');
    }
}
function endAjaxSearch() {
    searchesPending--;
    if (searchesPending == 0) {
        $('#search-ajax-loader').addClass('hidden');
    }
}

// Show modals
function showOrganizationModal() {
    orgData = $(this).data();
    if (orgData.latlng && orgData.latlng.length > 0) {
        // Get the lat, long values of the address
        searchedLatLng = new google.maps.LatLng(orgData.latlng[0], orgData.latlng[1]);
        plotOrganization(orgData);
    }
    else{
        if(marker){
            marker.setMap(null);
        }
        if (infowindow){
            infowindow.close();
        }

        var $modal = $('.modal').modal();
        createBootstrapModal($modal, '#bs-org-modal-template',orgData);
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

        if(marker){
            marker.setMap(null);
        }
        
        marker = new google.maps.Marker({
            map: map,
            position: coord
        });
        
        orgData.img_path = "/static/images/office_building_icon.png";

        var html = $("#modal-template").tmpl(data);

        if(infowindow){
            infowindow.close();
        }

        infowindow = new google.maps.InfoWindow({
		      content : html.html()
		});

        infowindow.open(map,marker);
        
        google.maps.event.addListener(marker, 'click', function() {
		    infowindow.open(map,marker);
		});

    } else {
        var $modal = $('.modal').modal();
        createBootstrapModal($modal, '#bs-org-modal-template', data);
    }
}

function createBootstrapModal(m, modal_template, data){
    // Do a bootstrap modal
    var html = $(modal_template).tmpl(data);

    $('#bs-modal').html(html);

    m.modal('show');
}

$(function(){
    initialize();
});
