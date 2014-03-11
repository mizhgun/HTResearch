/**
 * Provides an interface for various client-side validators.
 *
 * Should always take a DOM element (not a JQuery selector) for contractual consistency.
 *
 * @module validators
 */
define(function() {
    'use strict';

    /**
     * Checks a URL field for validity and prepends 'http://', if necessary.
     * @param {object} field The DOM field to be validated.
     */
    function checkURL(field) {
        var url = field.value;
        if (!(/^https?:\/\//.test(url))) {
            url = 'http://' + url;
        }
        field.value = url
    }

    return { checkURL: checkURL };
});