var searchResultsVisible = false;
var map;
var initialLatLng = new google.maps.LatLng(21, 78);
var searchedLatLng;
var address;
var orgData, contactData, pubData;
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

                $('#organization-results').css({
                    height: $('#organization-search-list').height()
                });

                setLinkClickEvents();
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

function plotOrganization(data) {
	if (data.latlng && data.latlng.length > 0 && data.latlng[0] != '' && data.latlng[1] != '') {
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

function setLinkClickEvents(){
    // the org link
    $('a.org_link').click(function(e){
        orgData = $(this).data();
        if (orgData.latlng) {
            // Get the lat, long values of the address
            searchedLatLng = new google.maps.LatLng(orgData.latlng[0], orgData.latlng[1]);
            plotOrganization(orgData);
        }
        else{
            var $modal = $('.modal').modal();
            createBootstrapModal($modal, '#bs-org-modal-template',orgData);
        }
    });

    // the contact link
    $('a.contact_link').click(function(e){
        contactData = $(this).data();
        var $modal = $('.modal').modal({
            show: false
        });
        createBootstrapModal($modal, '#bs-contact-modal-template', contactData);
    });

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
