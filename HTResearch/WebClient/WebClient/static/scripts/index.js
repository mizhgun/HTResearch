var searchResultsVisible = false;
var map;
var organizationImg = createImageHtml('static/images/office_building_icon.png');
var initialLatLng = new google.maps.LatLng(21,78);
var geocoder = new google.maps.Geocoder();
var dummyAddress = "9-10-11 Nehru Place, New Delhi - 110019 India";
var dummyContent = '<div id="content">'+
      '<div id="siteNotice">'+
      '</div>'+
      '<h3 id="firstHeading" class="firstHeading">Save the Children India</h3>'+
      '<div id="bodyContent">'+
      organizationImg+
      '<p>Tel: (+91) 11 4229 4900</p>'+
      '<p>Email: info@savethechildren.in</p>'+
      '<p>'+dummyAddress+'</p>'+
      '</div>'+
      '</div>';

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
	$('a').click(function(e){geocoder.geocode({'latLng': initialLatLng, 'address': dummyAddress}, plotOrganization)});
}

function showSearchResults() {
	if($('#search-box').val().length > 0 && !searchResultsVisible) {
		$('#search-results-div').toggle("slide", {
	        direction: "up",
	        distance: window.height - $('#search-box').css('top')
	    }, 500);

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

        var infowindow = new google.maps.InfoWindow({
		      content: dummyContent
		  });

        infowindow.open(map,marker);

        google.maps.event.addListener(marker, 'click', function() {
		    infowindow.open(map,marker);
		  });

      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
}

function createImageHtml(imgUrl) {
	return '<img src="'+imgUrl+'" class="col-md-3" style="margin-right: 10px;">';
}

google.maps.event.addDomListener(window, 'load', _.once(initialize));