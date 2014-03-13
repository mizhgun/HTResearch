define(['jquery', 'd3'], function($, d3) {

    function initialize(regionSelector, typeSelector, membersSelector, options) {
        var w = options.width || 300;
        var h = options.height || 300;
        var r = options.radius || 150;
        $.get('/orgs-by-region/', function(data) {
            data = data.data;

            var element = $(regionSelector);
            var color = d3.scale.category20c();

            var vis = d3.select(regionSelector)
                .append("svg:svg")
                .data([data])
                .attr('width', w)
                .attr('height', h)
                .append('svg:g')
                .attr('transform', 'translate(' + r + ',' + r + ')');

            var arc = d3.svg.arc()
                .outerRadius(r);

            var pie = d3.layout.pie()
                .value(function(d) { return d.value; });

            var arcs = vis.selectAll('g.slice')
                .data(pie)
                .enter()
                .append('svg:g')
                .attr('class', 'slice');

            arcs.append('svg:path')
                .attr('fill', function(d, i) { return color(i); } )
                .attr('d', arc);

            arcs.append('svg:text')
                .attr('transform', function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = r;
                    return 'translate(' + arc.centroid(d) + ')';
                })
                .attr('text-anchor', 'middle')
                .text(function(d, i) { return data[i].label; });

            element.append('<h2>Region</h2>');
        });

        $.get('/orgs-by-type/', function(data) {
            data = data.data;

            var element = $(typeSelector);
            var colors = [
                '#4ecdc4',
                '#c7f464',
                '#ff6b6b',
                '#888888'
            ];

            var vis = d3.select(typeSelector)
                .append('svg:svg')
                .data([data])
                .attr('width', w)
                .attr('height', h)
                .append('svg:g')
                .attr('transform', 'translate(' + r + ',' + r + ')');

            var arc = d3.svg.arc()
                .outerRadius(r);

            var pie = d3.layout.pie()
                .value(function(d) { return d.value; });

            var arcs = vis.selectAll("g.slice")
                .data(pie)
                .enter()
                .append('svg:g')
                .attr('class', 'slice');

            arcs.append('svg:path')
                .attr('fill', function(d, i) { return colors[i]; } )
                .attr('d', arc);

            arcs.append('svg:text')
                .attr("transform", function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = r;
                    return 'translate(' + arc.centroid(d) + ')';
                })
                .attr('text-anchor', 'middle')
                .text(function(d, i) { return data[i].label; });

            element.append('<h2>Type</h2>');
        });

        $.get('/orgs-by-members/', function(data) {
            data = data.data;

            var element = $(membersSelector);
            var color = d3.scale.category20c();

            var vis = d3.select(membersSelector)
                .append('svg:svg')
                .data([data])
                .attr('width', w)
                .attr('height', h)
                .append('svg:g')
                .attr('transform', 'translate(' + r + ',' + r + ')');

            var arc = d3.svg.arc()
                .outerRadius(r);

            var pie = d3.layout.pie()
                .value(function(d) { return d.value; });

            var arcs = vis.selectAll('g.slice')
                .data(pie)
                .enter()
                .append('svg:g')
                .attr('class', 'slice');

            arcs.append('svg:path')
                .attr('fill', function(d, i) { return color(i); } )
                .attr('d', arc);

            arcs.append('svg:text')
                .attr("transform", function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = r;
                    return 'translate(' + arc.centroid(d) + ')';
                })
                .attr('text-anchor', 'middle')
                .text(function(d, i) { return data[i].label; });

            element.append('<h2>Members</h2>');
        });
    }

    return { initialize: initialize };
});
