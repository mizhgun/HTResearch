var searchResultsVisible = false;
var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var geocoder = new google.maps.Geocoder();
var address;
var orgData = null;
var contactData = null;
var infowindow = null;
var marker = null;

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
	//var mapControls = new GLargeMapControl3D();
	//var bottomLeft = new GControlPosition(G_ANCHOR_BOTTOM_LEFT, new GSize(10,10));
	//map.removeControl(mapTypeControl)
	//map.addControl(mapControls, bottomLeft);

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
    $('#search-box').bind('keyup keypress', function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            e.preventDefault();
            return false;
        }
    });
	$('a.org_link').click(function(e){
        geocoder.geocode({'latLng': searchedLatLng, 'address': address}, plotOrganization)
    });
}

function showSearchResults() {
    var searchText = $('#search-box').val().trim();
    if(searchText) {
        // Search organizations
        startAjaxSearch();
        $.ajax({
            type: 'POST',
            url: '/search_organizations/',
            data: {
                'search_text': $('#search-box').val(),
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'html'
        }).done(function (data) {
            $('#organization-search-list').html(data);

            $('#organization-results').css({
                height: $('#organization-search-list').height()
            });

            var $modal = $('.modal').modal({
                show: false
            });
            $('.org_link').click(function(e){
                orgData = $(this).data();
                if (orgData.address) {
                    // Get the lat, long values of the address
                    geocoder.geocode({'address': orgData.address}, function(results, status){
                        if(results[0]){
                            lat = results[0].geometry.location.lat();
                            lng = results[0].geometry.location.lng();
                        }
                        searchedLatLng = new google.maps.LatLng(lat, lng);
                    });
                    geocoder.geocode({'latLng': searchedLatLng, 'address': orgData.address}, plotOrganization);
                }
                else{
                    bootstrapModal($modal);
                }
            });
        }).fail(function () {
            alert('THE (organization) SEARCH FAILED! BWAAHAHAHAHAHAAHAHAAHHAAAA TRAWLZ');
        }).always(function () {
            endAjaxSearch();
        });

        // Search contacts
        startAjaxSearch();
        $.ajax({
            type: 'POST',
            url: '/search_contacts/',
            data: {
                'search_text': $('#search-box').val(),
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'html'
        }).done(function (data) {
            $('#contact-search-list').html(data);

            $('#contact-results').css({
                height: $('#contact-search-list').height()
            });

            var $modal = $('.modal').modal({
                show: false
            });
            $('.contact_link').click(function(e){
                contactData = $(this).data();
                // TODO: display contact modal
            });
        }).fail(function () {
            alert('THE (contact) SEARCH FAILED! BWAAHAHAHAHAHAAHAHAAHHAAAA TRAWLZ');
        }).always(function () {
            endAjaxSearch();
        });

        if(!searchResultsVisible) {
            $('#search-results-div').toggle("slide", {
                direction: "up",
                distance: window.height - $('#search-box').css('top')
            }, 500);

            searchResultsVisible = true;
        }
	} else {
	    if (searchResultsVisible) {
	        $('#search-results-div').toggle('slide', {
	            direction: 'up',
	            distance: window.height - $('#search-box').css('top')
	        }, 500);

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

function plotOrganization(results, status) {
	if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);

        if(marker){
            marker.setMap(null);
        }
        
        marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location
        });
        
        orgData.img_path = "/static/images/office_building_icon.png";

        var html = $("#modal-template").tmpl(orgData);

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
        bootstrapModal($modal)
    }
}

function bootstrapModal(m){
    // Do a bootstrap modal
    var html = $("#bs-modal-template").tmpl(orgData);

    $('#bs-modal').html(html);

    m.modal('show');
}

google.maps.event.addDomListener(window, 'load', _.once(initialize));