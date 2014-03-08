define(['jquery', 'd3.fisheye', 'bootstrap'], function($, d3) {
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
        'PROT_PREV': 'url(#prot-prev-grad)',
        'PREV_PROS': 'url(#prev-pros-grad)',
        'PROS_PROT': 'url(#pros-prot-grad)',
        'ALL': 'url(#all-grad)'
    };


    function initialize(selector, options) {
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

        defs = svg.append('defs');

        defineGradients();

        d3.json('/partner-map/', function(error, graph) {
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
                .style('fill', function(d) { return map_types_to_color(d.types, graph.threeps) })
                .style('fill-opacity', 0.5)
                .on('mouseenter', function(e) { $(this).css('fill-opacity', 1.0) })
                .on('mouseleave', function(e) { $(this).css('fill-opacity', 0.5) });

            // Create legend.
            var legend = svg.append('g')
                .attr('class', 'legend')
                .attr('transform', 'translate(50,30)')
                .style('font-size', '12px')
                .call(createLegend, {
                    'Prevention': {
                        color: color.PREVENTION
                    },
                    'Protection': {
                        color: color.PROTECTION
                    },
                    'Prosecution': {
                        color: color.PROSECUTION
                    }
                });

            // Bind mousewheel to zoom.
            $(selector + ' svg').bind('DOMMouseScroll mousewheel', function(e) {
                e.preventDefault();
                zoomInOut(e);
            });

            svg.on("mousemove", function() {
              fisheye.focus(d3.mouse(this));

              node.each(function(d) { d.fisheye = fisheye(d); })
                  .attr("cx", function(d) { return d.fisheye.x; })
                  .attr("cy", function(d) { return d.fisheye.y; })
                  .attr('transform', function(d) {return 'translate(' + d.fisheye.x + ',' + d.fisheye.y +')'; })
                  .selectAll('circle')
                  .attr("r", function(d) { return d.fisheye.z * r; });

              link.attr("x1", function(d) { return d.source.fisheye.x; })
                  .attr("y1", function(d) { return d.source.fisheye.y; })
                  .attr("x2", function(d) { return d.target.fisheye.x; })
                  .attr("y2", function(d) { return d.target.fisheye.y; });
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

    function defineGradients() {
        var prot_prev_grad = defs.append('linearGradient').attr('id', 'prot-prev-grad')
            .attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
        prot_prev_grad.append('stop').attr('offset', '50%').style('stop-color', color.PROTECTION);
        prot_prev_grad.append('stop').attr('offset', '50%').style('stop-color', color.PREVENTION);

        var prev_pros_grad = defs.append('linearGradient').attr('id', 'prev-pros-grad')
            .attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
        prev_pros_grad.append('stop').attr('offset', '50%').style('stop-color', color.PREVENTION);
        prev_pros_grad.append('stop').attr('offset', '50%').style('stop-color', color.PROSECUTION);

        var pros_prot_grad = defs.append('linearGradient').attr('id', 'pros-prot-grad')
            .attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
        pros_prot_grad.append('stop').attr('offset', '50%').style('stop-color', color.PROSECUTION);
        pros_prot_grad.append('stop').attr('offset', '50%').style('stop-color', color.PROTECTION);

        var all_grad = defs.append('linearGradient').attr('id', 'all-grad')
            .attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
        all_grad.append('stop').attr('offset', '33%').style('stop-color', color.PROSECUTION);
        all_grad.append('stop').attr('offset', '33%').style('stop-color', color.PROTECTION);
        all_grad.append('stop').attr('offset', '67%').style('stop-color', color.PROTECTION);
        all_grad.append('stop').attr('offset', '67%').style('stop-color', color.PREVENTION);
    }

    function map_types_to_color(types, three_ps) {
        var has_prot = false;
        var has_pros = false;
        var has_prev = false;

        if (!types) {
            // return PREVENTION by default
            return color.PREVENTION;
        }

        // check for presence of each type
        _.each(types, function(type) {
            if (type === three_ps.PROTECTION)
                has_prot = true;
            if (type === three_ps.PROSECUTION)
                has_pros = true;
            if (type === three_ps.PREVENTION)
                has_prev = true;
        });

        if (has_prot && !has_pros && !has_prev)
            return color.PROTECTION;
        if (!has_prot && has_pros && !has_prev)
            return color.PROSECUTION;
        if (!has_prot && !has_pros && has_prev)
            return color.PREVENTION;
        if (has_prot && has_pros && !has_prev)
            return color.PROS_PROT;
        if (!has_prot && has_pros && has_prev)
            return color.PREV_PROS;
        if (has_prot && !has_pros && has_prev)
            return color.PROT_PREV;
        if (has_prot && has_pros && has_prev)
            return color.ALL;

        return color.PREVENTION;
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
