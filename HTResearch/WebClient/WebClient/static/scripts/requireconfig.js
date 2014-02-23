require.config({
    baseUrl: '/static/scripts/lib',
    paths: {
        index: '../index',
        contact: '../contact',
        organization: '../organization',
        shared: '../shared',
        user: '../user',
        fuelux: 'http://www.fuelcdn.com/fuelux/2.6.0/'
    },
    shim: {
        underscore: {
            exports: '_'
        },
        'jquery.tmpl': ['jquery'],
        'jquery.validate': ['jquery'],
        'jquery-ui': ['jquery'],
        'bootstrap': ['jquery'],
        'd3.layout.cloud': ['d3']
    }
});