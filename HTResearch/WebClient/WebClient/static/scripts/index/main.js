require.config({
    baseUrl: 'static/scripts/lib',
    paths: {
        index: '../index'
    },
    shim: {
        underscore: {
            exports: '_'
        },
        'jquery.tmpl': ['jquery'],
        'bootstrap': ['jquery']
    }
});

require(['index/index'], function(Index) {
    'use strict';

    Index.initialize();
});