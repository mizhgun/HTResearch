define(['jquery', 'd3', 'underscore'], function($, d3, _) {

    function initialize(regionSelector, typeSelector, membersSelector, options) {
        var w = options.width || 300;
        var h = options.height || 300;
        var r = options.radius || 150;

        // Move a selection to the front
        d3.selection.moveToFront = function() {
            return this.each(function() {
                this.parentNode.appendChild(this);
            })
        };

        function angle(d) {
            var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
            return a < 90 ? a : a - 180;
        }

        var emptyCategory = [
            {
                value: 100,
                label: '(no data)'
            }
        ];

        var visibilityThreshold = 0.02;

        var arc = d3.svg.arc()
            .innerRadius(r * 0.3)
            .outerRadius(r);

        var arcOver = d3.svg.arc()
            .innerRadius(r * 0.3)
            .outerRadius(r * 1.15);

        function arcMouseEnter(arcSel, data) {
            var curArc = d3.select(arcSel);
            var curArcData = curArc.data()[0].data;
            // Make slice grow
            curArc.select('path').transition()
                .duration(50)
                .attr('d', arcOver);
            // Make text bold, visible
            curArc.select('text')
                .style('font-weight', 'bold')
                .style('display', 'inherit');
            // Bring slice to the front
            curArc.each(function() {
                this.parentNode.appendChild(this);
            });
            d3.select(curArc.node().parentNode).select('.info1')
                .text(curArcData.label);
            d3.select(curArc.node().parentNode).select('.info2')
                .text(curArcData.value + ' out of ' + data.total +
                    ' (' + Math.round(curArcData.value / data.total * 100) + '%)');
        }
        function arcMouseLeave(arcSel, data) {
            var curArc = d3.select(arcSel);
            curArc.select('path').transition()
                .duration(200)
                .attr('d', arc);
            curArc.select('text')
                .style('font-weight', function(d) { return 'normal'; });
            if(isSkinny(curArc.data()[0].data, data)) {
                curArc.select('text').style('display', 'none');
            }
            // Clear label/count indicator
            d3.select(curArc.node().parentNode).select('.info1')
                .text('');
            d3.select(curArc.node().parentNode).select('.info2')
                .text('');
        }

        function isSkinny(d, data) {
            return d.value / data.total_known < visibilityThreshold;
        }

        $.get('/orgs-by-region/', function(data) {
            // If no organizations, indicate empty
            var categories = data.total ? data.categories : emptyCategory;

            var element = $(regionSelector);
            var color = d3.scale.category20c();

            var vis = d3.select(regionSelector)
                .append("svg:svg")
                .data([categories])
                .attr('width', w)
                .attr('height', h)
                .append('svg:g')
                .attr('transform', 'translate(' + w / 2 + ',' + (h - r * 1.15) + ')');

            var pie = d3.layout.pie()
                .value(function(d) { return d.value; });

            var arcs = vis.selectAll('g.slice')
                .data(pie)
                .enter()
                .append('svg:g')
                .attr('class', 'slice')
                .on('mouseenter', function(d) {
                    arcMouseEnter(this, data);
                })
                .on('mouseleave', function(d) {
                    arcMouseLeave(this, data);
                });

            arcs.append('svg:path')
                .attr('fill', function(d, i) { return color(i); } )
                .attr('d', arc);

            arcs.append('text')
                .attr('transform', function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = r;
                    return 'translate(' + arc.centroid(d) + ')rotate(' + angle(d) + ')translate(0,6)';
                })
                .attr('text-anchor', 'middle')
                .style('display', function(d) {
                    return isSkinny(d, data) ? 'none' : 'inherit';
                })
                .style('cursor', 'hand')
                .text(function(d, i) { return categories[i].label; });

            vis.append('foreignObject')
                .attr('width', 80)
                .attr('height', 80)
                .attr('transform', function(d) {
                    return 'translate(-40, -34)';
                })
                .html(function() {
                    return '<h1><i class="fa fa-globe"></i></h1>';
                });

            vis.append('svg:text')
                .attr('transform', function() {
                    return 'translate(0,-200)'
                })
                .attr('text-anchor', 'middle')
                .attr('class', 'info1')
                .style('font-weight', 'bold');
            vis.append('text')
                .attr('transform', function() {
                    return 'translate(0,-180)'
                })
                .attr('text-anchor', 'middle')
                .attr('class', 'info2');

            element.append('<h2>Region</h2>');
        });
        $.get('/orgs-by-type/', function(data) {
            // If no organizations, indicate empty
            var categories = data.total ? data.categories : emptyCategory;

            var element = $(typeSelector);
            var colors3p = {
                'protection': '#4ecdc4',
                'prevention': '#c7f464',
                'prosecution': '#ff6b6b'
            };

            var vis = d3.select(typeSelector)
                .append('svg:svg')
                .data([categories])
                .attr('width', w)
                .attr('height', h)
                .append('svg:g')
                .attr('transform', 'translate(' + w / 2 + ',' + (h - r * 1.15) + ')');

            var pie = d3.layout.pie()
                .value(function(d) { return d.value; });

            var arcs = vis.selectAll('g.slice')
                .data(pie)
                .enter()
                .append('svg:g')
                .attr('class', 'slice')
                .on('mouseenter', function(d) {
                    arcMouseEnter(this, data);
                })
                .on('mouseleave', function(d) {
                    arcMouseLeave(this, data);
                });

            function hex(x) {
                return ('0' + parseInt(x).toString(16)).slice(-2);
            }
            function grayscale(x) {
                return '#' + hex(x*255) + hex(x*255) + hex(x*255);
            }

            arcs.append('svg:path')
                .attr('fill', function(d, i) {
                    return colors3p[d.data.label.toLowerCase()]
                       || grayscale(0.4 + 0.6 * i / categories.length);
                })
                .attr('d', arc);

            arcs.append('svg:text')
                .attr('transform', function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = r;
                    return 'translate(' + arc.centroid(d) + ')rotate(' + angle(d) + ')translate(0,6)';
                })
                .attr('text-anchor', 'middle')
                .style('display', function(d) {
                    return isSkinny(d, data) ? 'none' : 'inherit';
                })
                .style('cursor', 'hand')
                .text(function(d, i) { return categories[i].label; });

            vis.append('foreignObject')
                .attr('width', 80)
                .attr('height', 80)
                .attr('transform', function(d) {
                    return 'translate(-40, -34)';
                })
                .html(function() {
                    return '<h1><i class="fa fa-gavel"></i></h1>';
                });

            vis.append('svg:text')
                .attr('transform', function() {
                    return 'translate(0,-200)'
                })
                .attr('text-anchor', 'middle')
                .attr('class', 'info1')
                .style('font-weight', 'bold');
            vis.append('text')
                .attr('transform', function() {
                    return 'translate(0,-180)'
                })
                .attr('text-anchor', 'middle')
                .attr('class', 'info2');

            element.append('<h2>Type</h2>');
        });
        $.get('/orgs-by-members/', function(data) {
            // If no organizations, indicate empty
            var categories = data.total ? data.categories : emptyCategory;

            var element = $(membersSelector);
            var color = d3.scale.category20c();

            var vis = d3.select(membersSelector)
                .append('svg:svg')
                .data([categories])
                .attr('width', w)
                .attr('height', h)
                .append('svg:g')
                .attr('transform', 'translate(' + w / 2 + ',' + (h - r * 1.15) + ')');

            var pie = d3.layout.pie()
                .value(function(d) { return d.value; });

            var arcs = vis.selectAll('g.slice')
                .data(pie)
                .enter()
                .append('svg:g')
                .attr('class', 'slice')
                .on('mouseenter', function(d) {
                    arcMouseEnter(this, data);
                })
                .on('mouseleave', function(d) {
                    arcMouseLeave(this, data);
                });

            arcs.append('svg:path')
                .attr('fill', function(d, i) { return color(i); } )
                .attr('d', arc);

            arcs.append('svg:text')
                .attr("transform", function(d) {
                    d.innerRadius = 0;
                    d.outerRadius = r;
                    return 'translate(' + arc.centroid(d) + ')rotate(' + angle(d) + ')translate(0,6)';
                })
                .attr('text-anchor', 'middle')
                .style('display', function(d) {
                    return isSkinny(d, data) ? 'none' : 'inherit';
                })
                .style('cursor', 'hand')
                .text(function(d, i) { return categories[i].label; });

            vis.append('foreignObject')
                .attr('width', 80)
                .attr('height', 80)
                .attr('transform', function(d) {
                    return 'translate(-40, -34)';
                })
                .html(function() {
                    return '<h1><i class="fa fa-users"></i></h1>';
                });

            vis.append('svg:text')
                .attr('transform', function() {
                    return 'translate(0,-200)'
                })
                .attr('text-anchor', 'middle')
                .attr('class', 'info1')
                .style('font-weight', 'bold');
            vis.append('text')
                .attr('transform', function() {
                    return 'translate(0,-180)'
                })
                .attr('text-anchor', 'middle')
                .attr('class', 'info2');

            element.append('<h2>Members</h2>');
        });
    }

    return { initialize: initialize };
});
