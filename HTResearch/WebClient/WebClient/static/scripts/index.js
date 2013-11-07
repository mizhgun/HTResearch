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
	$('a').click(function(e){geocoder.geocode({'latLng': initialLatLng, 'address': dummyAddress}, plotOrganization)});
}

function showSearchResults() {
    var searchText = $('#search-box').val();
    if(searchText) {
        $.ajax({
            type: 'POST',
            url: '/search/',
            data: {
                'search_text': $('#search-box').val(),
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                $('#organization-search-list').html(data);
            },
            dataType: 'html'
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
            'addr': address,
            'org_id': 4
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

function createImageHtml(imgUrl) {
	return '<img src="'+imgUrl+'" class="col-md-3" style="margin-right: 10px;">';
}

google.maps.event.addDomListener(window, 'load', _.once(initialize));