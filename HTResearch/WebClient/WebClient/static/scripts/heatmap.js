/**
 * NOTE: This file requires that the google map be included before it, as it has
 * a dependency on the google map object. Currently, this is a variable called
 * map.
 */

var orgCoordinates = [];
var heatMap;
var heatMapGradient = [
    'rgba(0, 255, 255, 0)',
    'rgba(0, 255, 255, 1)',
    'rgba(0, 191, 255, 1)',
    'rgba(0, 127, 255, 1)',
    'rgba(0, 63, 255, 1)',
    'rgba(0, 0, 255, 1)',
    'rgba(0, 0, 223, 1)',
    'rgba(0, 0, 191, 1)',
    'rgba(0, 0, 159, 1)',
    'rgba(0, 0, 127, 1)',
    'rgba(63, 0, 91, 1)',
    'rgba(127, 0, 63, 1)',
    'rgba(191, 0, 31, 1)',
    'rgba(255, 0, 0, 1)'
];
var heatMapRadius = 15;

function createHeatMap() {
    var pointArray = new google.maps.MVCArray(orgCoordinates);
    heatMap = new google.maps.visualization.HeatmapLayer({
        data: pointArray,
        radius: heatMapRadius,
        gradient: heatMapGradient
    });
};

function loadCoordinates(success_cb) {
    // Clear array
    orgCoordinates.length = 0;
    var geocoder = new google.maps.Geocoder();

    $.ajax({
        type: 'POST',
        url: '/heatmap_coordinates/',
        data: {
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function ( json_string ) {
            var addresses = $.parseJSON(json_string);
            var i;
            for (i = 0; i < addresses.length; i++) {
                addr = addresses[i];
                geocoder.geocode({'address': addr}, function(results, status){
                    var lat; var lng;
                    if(status == google.maps.GeocoderStatus.OK){
                        lat = results[0].geometry.location.lat();
                        lng = results[0].geometry.location.lng();
                        var gCoord = new google.maps.LatLng(lat, lng);
                        orgCoordinates.push(gCoord);
                        // Rebuild heatmap
                        success_cb();
                    }
                });
            }
        },
        dataType: 'html'
    });
}

function initHeatmap() {
    // call load coordinates with a callback to createHeatMap
    loadCoordinates(createHeatMap);
}

function toggleHeatMap() {
    // map is a variable from the file index.js
    if (heatMap != null) {
        heatMap.setMap(heatMap.getMap() ? null : map);
    }
}

$(window).load(function() {
    initHeatmap();

    var heatmap_control_div = document.createElement('div');

    var heatmap_toggle_control = document.createElement('button');
    $(heatmap_toggle_control).addClass('btn');
    $(heatmap_toggle_control).addClass('btn-default');
    $(heatmap_toggle_control).addClass('btn-sm');
    $(heatmap_toggle_control).text('Toggle Heat Map');
    heatmap_control_div.appendChild(heatmap_toggle_control)

    google.maps.event.addDomListener(heatmap_toggle_control, 'click', function(){
        $(this).attr("disabled", "true");
        toggleHeatMap();
        $(this).removeAttr("disabled");
    });
    heatmap_control_div.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(heatmap_control_div);
});