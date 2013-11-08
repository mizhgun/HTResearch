var searchResultsVisible = false;
var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var geocoder = new google.maps.Geocoder();
var address;
var orgData;

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
                var $modal = $('.modal').modal({
                    show: false
                });
                $('a.org_link').click(function(e){
                    orgData = $(this).data();
                    if (orgData.address != '') {
                        // Get the lat, long values of the address
                        geocoder.geocode({'address': orgData.address}, function(results, status){
                            lat = results[0].geometry.location.lat();
                            lng = results[0].geometry.location.lng();
                            searchedLatLng = new google.maps.LatLng(lat, lng);
                        });
                        geocoder.geocode({'latLng': searchedLatLng, 'address': orgData.address}, plotOrganization);
                    }
                    else{
                        bootstrapModal($modal)
                    }
                });
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
        
        orgData.img_path = "/static/images/office_building_icon.png";

        var html = $("#modal-template").tmpl(orgData);

        var infowindow = new google.maps.InfoWindow({
		      content : html.html()
		});

        infowindow.open(map,marker);
        
        google.maps.event.addListener(marker, 'click', function() {
		    infowindow.open(map,marker);
		});

    } else {
        var $modal = $('.modal').modal({
            show: false
        });
        bootstrapModal($modal)
    }
}

function bootstrapModal(m){
    // Do a bootstrap modal
    $('#modal-header').text(orgData.name);

    var html = '<table class="table-condensed"><tr class="modal-row"><td>Tel:</td><td>';

    if (orgData['phone_numbers'].length == 0){
        html += 'None';
    } else {
        for (var i=0; i < orgData['phone_numbers'].length; i++){
            html += orgData['phone_numbers'][i] + '</br>'
        }
    }

    html += '</td></tr><tr class="modal-row"><td>Email:</td><td>';

    if (orgData['emails'].length == 0){
        html += 'None'
    } else {
        for (var i=0; i < orgData['emails'].length; i++){
            html += orgData['emails'][i] + '</br>';
        }
    }

    html += '</td></tr><tr class="modal-row"><td>Address:</td><td>';

    if (orgData.address == ''){
        html += 'None';
    } else {
        html += orgData.address;
    }

    html += '</td></tr></table><a id="moreInfo" href="/organization/' + orgData.id + '">More Info</a>';


    $('#modal-body').html(html);
    m.modal('show');
}

google.maps.event.addDomListener(window, 'load', _.once(initialize));