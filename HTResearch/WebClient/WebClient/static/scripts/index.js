var searchResultsVisible = false;

function initialize() {
	var mapOptions = {
	  center: new google.maps.LatLng(21, 78),
	  zoom: 5,
	  mapTypeId: google.maps.MapTypeId.ROADMAP,
	  panControl: false,
	  zoomControl: false,
	  scaleControl: false,
	};

	var map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);
	//var mapControls = new GLargeMapControl3D();
	//var bottomLeft = new GControlPosition(G_ANCHOR_BOTTOM_LEFT, new GSize(10,10));
	//map.removeControl(mapTypeControl)
	//map.addControl(mapControls, bottomLeft);

	$('#signup-btn').click(function(e) {
		$('#signup-div').easyModal({
			autoOpen: true,
			overlayOpacity: 0.3,
			overlayColor: "#333",
			overlayClose: false
		});

	});

	$('#login-btn').click(function(e) {
		$('#login-div').easyModal({
			autoOpen: true,
			overlayOpacity: 0.3,
			overlayColor: "#333",
			overlayClose: false
		});

	});

	$('#search-box').keypress(_.debounce(showSearchResults, 300));
	$('#search-box').keyup(_.debounce(hideSearchResults, 100));
}

function showSearchResults() {
	if($('#search-box').val().length > 0 && searchResultsVisible == false) {
		$('#search-results-div').toggle("slide", {
	        direction: "up",
	        distance: window.height - $('#search-box').css('top')
	    }, 500);

		searchResultsVisible = true;
	}
}

function hideSearchResults(e) {
	//Falsy bullcrap
	if($('#search-box').val().length == 0 && searchResultsVisible == true) {
		$('#search-results-div').toggle("slide", {
	        direction: "up",
	        distance: window.height - $('#search-box').css('top')
	    }, 500);

		searchResultsVisible = false;
	}
}

google.maps.event.addDomListener(window, 'load', _.once(initialize));