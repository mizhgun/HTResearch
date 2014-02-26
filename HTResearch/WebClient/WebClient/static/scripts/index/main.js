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
        'bootstrap': {
            deps: ['jquery']
        }
    }
});

require(['index/index'], function(Index) {
    'use strict';

    Index.initialize();
});