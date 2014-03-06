require.config({
    baseUrl: '/static/scripts/lib',
    paths: {
        index: '../index',
        contact: '../contact',
        datavis: '../data-vis',
        organization: '../organization',
        shared: '../shared',
        user: '../user',
        fuelux: 'http://www.fuelcdn.com/fuelux/2.6.0/',
        d3: "d3"
    },
    shim: {
        underscore: {
            exports: '_'
        },
        'jquery.tmpl': ['jquery'],
        'jquery.validate': ['jquery'],
        'jquery-ui': ['jquery'],
        'bootstrap': [
            'jquery',
            'jquery-ui'
        ],
        'd3.layout.cloud': ['d3_v2.7.4']
    }
});

require(['shared/media-sharing'], function(MediaSharing) {
    MediaSharing.initialize();
});
