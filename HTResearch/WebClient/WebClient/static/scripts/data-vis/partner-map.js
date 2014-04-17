/**
 * Provides a means of initializing the graph of organizations and their partners.
 *
 * @module partner-map
 */
define(['jquery', 'd3.fisheye', 'bootstrap'], function($, d3) {
    'use strict';

    var gradients = [];

    var width = window.innerWidth,
        height = window.innerHeight;

    var fisheye = d3.fisheye.circular()
        .radius(200)
        .distortion(2);

    var force = d3.layout.force()
        .charge(-5000)
        .gravity(3.0)
        .friction(0.3)
        .linkDistance(30);

    var svg,
        defs,
        nodeCount,
        r;

    var color = {
        'PROTECTION': '#FF6B64',
        'PREVENTION': '#4ECDC4',
        'PROSECUTION': '#C7F464',
        'ADVOCACY': '#006600',
        'EDUCATION': '#EF843C',
        'GOVERNMENT': '#EAB839',
        'NGO': '#7EB26D',
        'RELIGIOUS': '#7EB26D',
        'RESEARCH': '#705DA0',
        'UNKNOWN': '#BA43A9'
    };

    /**
     * Initializes the partner map.
     * @param {string} selector The selector of the DOM element to use for instantiation.
     * @param {object} options The options object associated with instantiation (width, height).
     */
    function initialize(selector, options) {
        var width = $(selector).width(), height = 0;
        if (options) {
            if (options.width){
                width = options.width;
            }
            if (options.height) {
                height = options.height;
            }
        }

        svg = d3.select(selector).append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'partner-map-svg')
            .attr('overflow', 'scroll');

        $(window).resize(function() {
            d3.select(selector).select('svg')
                .attr('width', $(selector).width());
            force.size([$(selector).width(), height]);
        });

        defs = svg.append('defs');

        d3.json('/api/partner-map/', function(error, graph) {
            // start d3.layout.force
            force
                .nodes(graph.nodes)
                .links(graph.links)
                .size([width, height]);

            nodeCount = graph.nodes.length;

            // Create links for nodes
            var link = svg.selectAll('.link')
                .data(graph.links)
                .enter().append('line')
                .attr('class', 'link')
                .style('stroke', '#999')
                .style('stroke-opacity', 6)
                .style('stroke-width', 2);

            // Create nodes which are svg:g elements containing node data.
            var node = svg.selectAll('.node')
                .data(graph.nodes)
                .enter().append('svg:g')
                .attr('id', function(d) { return d.id; })
                .attr('class', 'node')
                .attr('transform', function(d) {return 'translate(' + d.x + ',' + d.y +')'; })
                .attr('data-toggle', 'popover')
                .style('cursor', 'pointer')
                .on('click', function(e) {
                    var url = '/organization/' + $(this).attr('id');
                    window.open(url);
                })
                .each(
                    function(d,i) {
                        $(this).popover({
                            content: create_popover_content(d),
                            container: 'body',
                            delay: {
                                show: 250,
                                hide: 100
                            },
                            html: true,
                            placement: 'auto top',
                            trigger: 'hover'
                        })
                    }
                );

            r = 15;

            // Add circles for every node
            node.append('svg:circle').attr('r', 15)
                .style('stroke', '#fff')
                .style('stroke-width', '1.5px')
                .style('fill', function(d) { return map_types_to_color(d.types, graph.types) })
                .style('fill-opacity', 0.5)
                .on('mouseenter', function(e) { $(this).css('fill-opacity', 1.0) })
                .on('mouseleave', function(e) { $(this).css('fill-opacity', 0.5) });

            // Create legend.
            var legend = svg.append('g')
                .attr('class', 'legend')
                .attr('transform', 'translate(50,30)')
                .style('font-size', '12px')
                .call(createLegend, {
                    'Advocacy': {
                        color: color.ADVOCACY
                    },
                    'Education': {
                        color: color.EDUCATION
                    },
                    'Government': {
                        color: color.GOVERNMENT
                    },
                    'NGO': {
                        color: color.NGO
                    },
                    'Prevention': {
                        color: color.PREVENTION
                    },
                    'Prosecution': {
                        color: color.PROSECUTION
                    },
                    'Protection': {
                        color: color.PROTECTION
                    },
                    'Religious': {
                        color: color.RELIGIOUS
                    },
                    'Research': {
                        color: color.RESEARCH
                    },
                    'Unknown': {
                        color: color.UNKNOWN
                    }
                });

            // Bind mousewheel to zoom.
            $(selector + ' svg').bind('DOMMouseScroll mousewheel', function(e) {
                e.preventDefault();
                zoomInOut(e);
            });

            force.on('tick', function() {
                link.attr('x1', function(d) { return d.source.x; })
                    .attr('y1', function(d) { return d.source.y; })
                    .attr('x2', function(d) { return d.target.x; })
                    .attr('y2', function(d) { return d.target.y; });

                node.attr('cx', function(d) { return d.x; })
                    .attr('cy', function(d) { return d.y; })
                    .attr('transform', function(d) {return 'translate(' + d.x + ',' + d.y +')'; });
            });

            startStopForce();
        });
    }

    function startStopForce() {
        force.start();
    }

    function createLegend(g, items) {
        g.each(function() {
            var g= d3.select(this),
                svg = d3.select(g.property('nearestViewportElement')),
                legendPadding = g.attr('data-style-padding') || 5,
                lb = g.selectAll('.legend-box').data([true]),
                li = g.selectAll('.legend-items').data([true]);

            lb.enter().append('rect').classed('legend-box',true).attr('fill', 'white').attr('stroke', 'black');
            li.enter().append('g').classed('legend-items',true);

            items = d3.entries(items).sort(function(a,b) { return a.value.pos-b.value.pos});

            li.selectAll('text')
                .data(items,function(d) { return d.key})
                .call(function(d) { d.enter().append('text')})
                .call(function(d) { d.exit().remove()})
                .attr('y',function(d,i) { return i+'em'})
                .attr('x','1em')
                .text(function(d) { return d.key});

            li.selectAll('circle')
                .data(items,function(d) { return d.key})
                .call(function(d) { d.enter().append('circle')})
                .call(function(d) { d.exit().remove()})
                .attr('cy',function(d,i) { return i-0.25+'em'})
                .attr('cx',0)
                .attr('r','0.4em')
                .style('fill',function(d) { return d.value.color});

            // Reposition and resize the box
            var lbbox = li[0][0].getBBox();
            lb.attr('x',(lbbox.x-legendPadding))
                .attr('y',(lbbox.y-legendPadding))
                .attr('height',(lbbox.height+2*legendPadding))
                .attr('width',(lbbox.width+2*legendPadding));
      });
      return g;
    }

    function create_popover_content(node) {
        return '<h4>' + node.name + '</h4>' + (node.addr ? '<i>' + node.addr + '</i>' : '');
    }

    function defineSingleGradient(typeName) {
        return color[typeName];
    }

    function defineDoubleGradient(typeName1, typeName2) {
        var color1 = color[typeName1];
        var color2 = color[typeName2];

        var gradId = typeName1 + '-' + typeName2 + '-grad';
        var gradUrl = 'url(#' + gradId + ')';

        var grad = defs.append('linearGradient').attr('id', gradId)
            .attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
        grad.append('stop').attr('offset', '50%').style('stop-color', color1);
        grad.append('stop').attr('offset', '50%').style('stop-color', color2);

        return gradUrl;
    }

    function defineTripleGradient(typeName1, typeName2, typeName3) {
        var color1 = color[typeName1];
        var color2 = color[typeName2];
        var color3 = color[typeName3];

        var gradId = typeName1 + '-' + typeName2 + '-' + typeName3 + '-grad';
        var gradUrl = 'url(#' + gradId + ')';

        var all_grad = defs.append('linearGradient').attr('id', gradId)
            .attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
        all_grad.append('stop').attr('offset', '33%').style('stop-color', color1);
        all_grad.append('stop').attr('offset', '33%').style('stop-color', color2);
        all_grad.append('stop').attr('offset', '67%').style('stop-color', color2);
        all_grad.append('stop').attr('offset', '67%').style('stop-color', color3);

        return gradUrl;
    }

    function defineGradient(typeName1, typeName2, typeName3) {
        if (typeName2 === 'UNKNOWN')
            return defineSingleGradient(typeName1);
        if (typeName3 === 'UNKNOWN')
            return defineDoubleGradient(typeName1, typeName2);

        return defineTripleGradient(typeName1, typeName2, typeName3);
    }

    function map_types_to_color(types, type_maps) {
        function getKeyByValue(hash, value) {
            var key;
            for (key in hash) {
                if (hash[key] === value) return key;
            }
        }

        var type_count = types.length;
        types.sort(function (a, b) {
            var aType = getKeyByValue(type_maps, a);
            var bType = getKeyByValue(type_maps, b);

            // Prevention, Protection, and Prosecution are most important
            // Unknown is least important
            if (aType === 'PREVENTION')
                return -1;
            else if (bType === 'PREVENTION')
                return 1;
            else if (a === 'PROTECTION')
                return -1;
            else if (b === 'PROTECTION')
                return 1;
            else if (a === 'PROSECUTION')
                return -1;
            else if (b === 'PROSECUTION')
                return 1;
            else if (a === 'UNKNOWN')
                return 1; // b is first
            else if (b === 'UNKNOWN')
                return -1; // a is first

            return aType > bType ? 1 : -1;
        });

        var type1 = type_maps.UNKNOWN;
        var type2 = type_maps.UNKNOWN;
        var type3 = type_maps.UNKNOWN;

        if (type_count > 0) {
            type1 = types[0];
            if (type_count > 1) {
                type2 = types[1];
                if (type_count > 2)
                    type3 = types[2];
            }
        }

        var typeName1 =  getKeyByValue(type_maps, type1);
        var typeName2 =  getKeyByValue(type_maps, type2);
        var typeName3 =  getKeyByValue(type_maps, type3);

        // If already generated, return it
        if (gradients && gradients[type1] && gradients[type1][type2] && gradients[type1][type2][type3])
            return gradients[type1][type2][type3];

        // Make sure parent arrays are initialized
        if (!gradients)
            gradients = [];
        if (!gradients[type1])
            gradients[type1] = [];
        if (!gradients[type1][type2])
            gradients[type1][type2] = [];

        gradients[type1][type2][type3] = defineGradient(typeName1, typeName2, typeName3);
        return gradients[type1][type2][type3];
    }

    function zoomInOut(evt) {
        var curCharge = force.charge();
        if(evt.originalEvent.wheelDelta > 0) {
            r++;
            $('.node circle').attr('r', r);
            force.charge(curCharge - 500);
            startStopForce();
        } else {
            if (r > 1 && curCharge + 500 < 0) {
                r--;
                $('.node circle').attr('r', r);
                force.charge(curCharge + 500);
                startStopForce();
            }
        }
    }

    return { initialize: initialize };
});
