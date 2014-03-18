/**
 * Main script for the welcome page. Creates a cookie to mark a user's initial visit
 */

require(['jquery'], function($) {
    'use strict';

    $('.btn').click(function () {
        var expire = new Date();
        expire = new Date(expire.getTime() + 7776000000);
        document.cookie = "htresearchv2=amaterasu; path=/; expires=" + expire;

        window.location = '/get-started/';
    });
});