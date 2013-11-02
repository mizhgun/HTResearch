var searchResultsVisible = false;
var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var geocoder = new google.maps.Geocoder();
var address;

function initialize() {
	var mapOptions = {
	  center: initialLatLng,
	  zoom: 5,
	  mapTypeId: google.maps.MapTypeId.ROADMAP,
	  panControl: false,
	  zoomControl: false,
	  scaleControl: false,
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

	$('#search-box').keypress(_.debounce(showSearchResults, 300));
	$('#search-box').keyup(_.debounce(hideSearchResults, 100));
	$('a.org_link').click(function(e){
        geocoder.geocode({'latLng': searchedLatLng, 'address': address}, plotOrganization)
    });
}

function showSearchResults() {
	if($('#search-box').val().length > 0 && !searchResultsVisible) {
		$('#search-results-div').toggle("slide", {
	        direction: "up",
	        distance: window.height - $('#search-box').css('top')
	    }, 500);
        
        // Need to get the address based on the search results
        address = '9-10-11 Nehru Place, New Delhi - 110019 India';
        
        // Get the lat, long values of the address
        geocoder.geocode({'address': address}, function(results, status){
            lat = results[0].geometry.location.lat();
            lng = results[0].geometry.location.lng();
            searchedLatLng = new google.maps.LatLng(lat, lng);
        });
		searchResultsVisible = true;
	}
}

function hideSearchResults(e) {
	//Falsy bullcrap
	if($('#search-box').val().length === 0 && searchResultsVisible) {
		$('#search-results-div').toggle("slide", {
	        direction: "up",
	        distance: window.height - $('#search-box').css('top')
	    }, 500);

		searchResultsVisible = false;
	}
}

function plotOrganization(results, status) {
	if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location
        });
        
        // the values will be replaced by results from the search
        var org = {
            'org_name': 'Save The Children India', 
            'img_path': 'static/images/office_building_icon.png',
            'phone_num': '(+91) 11 4229 4900',
            'org_email': 'info@savethechildren.in',
            'addr': address
        };
        
        html = $("#modal-template").tmpl(org);
        
        var infowindow = new google.maps.InfoWindow({
		      content : html.html()
		  });

        infowindow.open(map,marker);

        google.maps.event.addListener(marker, 'click', function() {
		    infowindow.open(map,marker);
		  });

      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
}

google.maps.event.addDomListener(window, 'load', _.once(initialize));