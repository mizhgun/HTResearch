/**
 * Provides an abstraction for a Google Maps instance.
 *
 * @module map
 */
define(['jquery',
        'jquery.tmpl',
        'async!https://maps.googleapis.com/maps/api/js?sensor=false&libraries=visualization'], function($) {
   'use strict';

    var MARKER_VALUES = {
        PREVENTION: 1 << 0,
        PROTECTION: 1 << 1,
        PROSECUTION: 1 << 2
    };

    var INITIAL_LATLNG = new google.maps.LatLng(21, 78);

    /**
     * An encapsulation of the Google Maps object.
     * @param {string} element The DOM element associated with the Google Maps object.
     * @alias module:map
     * @constructor
     */
    var Map = function(element) {
        var options = {
            center: INITIAL_LATLNG,
            zoom: 5,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.TOP_LEFT
            },
            panControl: false,
            zoomControl: true,
            zoomControlOptions: {
              position: google.maps.ControlPosition.LEFT_TOP,
            },
            scaleControl: false,
            streetViewControl: false
        };

        this.map = new google.maps.Map(element, options);
        this.markers = [];
    };

    Map.prototype = {
        /**
         * Binds a function to a specified event on the Google Map.
         * @param {string} event The event string to bind.
         * @param {function} func The callback to bind to the event.
         */
        bind: function(event, func) {
            google.maps.event.addListener(this.map, event, func);
        },
        /**
         * Returns the encapsulated Google Map instance.
         * @returns {object} The Google Map instance.
         */
        getMap: function() {
            return this.map;
        },
        /**
         * Displays info regarding an organization on the map.
         * @param {object} data The JSON serialization of an Organization model.
         */
        showInfo: function(data) {
            var coord = new google.maps.LatLng(data.latlng[0], data.latlng[1]);
            this.map.setCenter(coord);

            this.closeAllInfowindows();

            var marker = this.findMarkerById(data.id);

            marker.infowindow.open(this.map, marker.marker);
            marker.open = true;
        },
        /**
         * Pushes a new control to the Google Map instance.
         * @param {object} position The position for the new control.
         * @param {object} control The maps control to be added.
         */
        pushControl: function(position, control) {
            this.map.controls[position].push(control);
        },
        /**
         * Removes all Markers from the map.
         */
        removeAllMarkers: function() {
            $.each(this.markers, function (index, value) {
                value.marker.setMap(null);
            });
            this.markers = [];
        },
        /**
         * Resize controls on map
         */
        resizeControls: function() {
            var p = google.maps.ControlPosition;
            var mapHeight = $(this.map.getDiv()).height();
            var scaleHeight = mapHeight/600.0;
            var mapWidth = $(this.map.getDiv()).width();
            var scaleWidth = mapWidth/720.0;
            var scaleTot = Math.min(scaleHeight, scaleWidth);
            scaleTot = Math.max(scaleTot, 1.0)
            var transOrigin = "";
            this.map.controls.forEach( function(posControls, index){
                if (index == p.TOP_LEFT || index == p.LEFT_TOP || index == p.TOP_CENTER || index == p.LEFT_CENTER)
                    transOrigin = "0% 0%";
                else if (index == p.LEFT_BOTTOM || index == p.BOTTOM_LEFT || index == p.BOTTOM_CENTER)
                    transOrigin = "0% 100%";
                else if (index == p.BOTTOM_RIGHT || index == p.RIGHT_BOTTOM)
                    transOrigin = "100% 100%";
                else
                    transOrigin = "100% 0%";
                posControls.forEach(function (control, index2) {
                    $(control).css("transform", "scale(" + scaleTot  + ")");
                    $(control).css("transform-origin", transOrigin);
                    $(control).css("-ms-transform", "scale(" + scaleTot  + ")");
                    $(control).css("-ms-transform-origin", transOrigin);
                    $(control).css("-webkit-transform", "scale(" + scaleTot  + ")");
                    $(control).css("-webkit-transform-origin", transOrigin);
                });
            });
        },
        /**
         * Closes all opened InfoWindows on the map.
         */
        closeAllInfowindows: function() {
            $.each(this.markers, function (index, value) {
                value.infowindow.close();
                value.open = false;
            });
        },
        /**
         * Finds a Marker in the currently registered list of markers on the map.
         * @param {object} marker The Marker to be found.
         * @returns {object} The stored Marker.
         */
        findMarker: function(marker) {
            var retMarker;
            for (var i = 0; i < this.markers.length; i++) {
                if (marker === this.markers[i].marker) {
                    retMarker = this.markers[i];
                    break;
                }
            }
            return retMarker;
        },
        /**
         * Finds a Marker in the currently registered list of markers, by its id.
         * @param {number} id The ID associated with the Marker.
         * @returns {object} The stored Marker.
         */
        findMarkerById: function(id) {
            var marker;
            for (var i = 0; i < this.markers.length; i++) {
                if (id === this.markers[i].id) {
                    marker = this.markers[i];
                    break;
                }
            }
            return marker;
        },
        /**
         * Plots a new Marker object on the map associated with an organization.
         * @param {object} data The JSON serialization of an Organization model.
         */
        plotMarker: function(data) {
            var self = this;
            if (data.latlng && data.latlng.length > 0 && data.latlng[0] && data.latlng[1]) {
                var coord = new google.maps.LatLng(data.latlng[0], data.latlng[1]);

                var marker_url = "";
                var is_prev = $.inArray(5, data.types) > -1; // Value for prevention enum
                var is_prot = $.inArray(6, data.types) > -1; // Value for protection enum
                var is_pros = $.inArray(7, data.types) > -1; // Value for prosecution enum
                var marker_switch = 0;
                if (is_prev)
                    marker_switch |= MARKER_VALUES.PREVENTION;
                if (is_prot)
                    marker_switch |= MARKER_VALUES.PROTECTION;
                if (is_pros)
                    marker_switch |= MARKER_VALUES.PROSECUTION;
                switch (marker_switch) {
                    case MARKER_VALUES.PREVENTION: //Prevention only
                        marker_url = "/static/images/prevention_pin_small.png"
                        break;
                    case MARKER_VALUES.PROTECTION: //Protection only
                        marker_url = "/static/images/protection_pin_small.png"
                        break;
                    case (MARKER_VALUES.PREVENTION | MARKER_VALUES.PROTECTION): //Prevention and Protection
                        marker_url = "/static/images/prot_prev_pin_small.png"
                        break;
                    case MARKER_VALUES.PROSECUTION: //Prosecution only
                        marker_url = "/static/images/prosecution_pin_small.png"
                        break;
                    case (MARKER_VALUES.PREVENTION | MARKER_VALUES.PROSECUTION): //Prevention and Prosecution
                        marker_url = "/static/images/prev_pros_pin_small.png"
                        break;
                    case (MARKER_VALUES.PROTECTION | MARKER_VALUES.PROSECUTION): //Protection and Prosecution
                        marker_url = "/static/images/prot_pros_pin_small.png"
                        break;
                    case (MARKER_VALUES.PREVENTION | MARKER_VALUES.PROTECTION | MARKER_VALUES.PROSECUTION): //All
                        marker_url = "/static/images/all_pin_small.png"
                        break;
                    default: // keep default
                        marker_url = "/static/images/default_pin_small.png";
                        break;
                }

                var new_marker = new google.maps.Marker({
                    map: self.map,
                    position: coord,
                    icon: {
                        url: marker_url,
                        size: new google.maps.Size(39, 32),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(9, 32)
                    }
                });

                data.img_path = "/static/images/office_building_icon.png";
                var html = $("#modal-template").tmpl(data);

                var new_infowindow = new google.maps.InfoWindow({
                    content: html.html()
                });

                google.maps.event.addListener(new_marker, 'click', function () {
                    var thisMarker = self.findMarker(new_marker);
                    if (!thisMarker) {
                        new_infowindow.open(this.map, new_marker);
                        self.closeAllInfowindows();
                    } else if (thisMarker.open) {
                        self.closeAllInfowindows();
                        thisMarker.infowindow.close();
                        thisMarker.open = false;
                    } else {
                        self.closeAllInfowindows();
                        thisMarker.infowindow.open(this.map, new_marker);
                        thisMarker.open = true;
                    }
                });

                this.markers.push({
                    id: data.id,
                    marker: new_marker,
                    infowindow: new_infowindow,
                    open: false
                });
            }
        }
    };

    return Map;
});