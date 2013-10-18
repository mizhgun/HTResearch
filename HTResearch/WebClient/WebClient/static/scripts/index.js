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

	$("#signup-btn").click(function(e) {
		$('#test-div').show().animate({top: $("#test-div").parent().height() / 3 - $("#test-div").height() / 3, 
			left: $("#test-div").parent().width() / 2 - $("#test-div").width() / 2}, 300);
	});
}

google.maps.event.addDomListener(window, 'load', initialize);