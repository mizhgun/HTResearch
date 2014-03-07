define(['jquery', 'd3', 'bootstrap'], function($, d3) {
    var width = window.innerWidth,
        height = window.innerHeight;

    var force = d3.layout.force()
        .charge(-5000)
        .gravity(3.0)
        .friction(0.3)
        .linkDistance(30)
        .size([width, height]);

    var svg = d3.select('body').append('svg')
        .attr('id', 'viewport')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'partner-map-svg')
        .attr('overflow', 'scroll');

    var defs = svg.append('defs');

    var color = {
        'PROTECTION': '#FF6B64',
        'PREVENTION': '#4ECDC4',
        'PROSECUTION': '#C7F464'
    };

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

    color['PROT_PREV'] = 'url(#prot-prev-grad)';
    color['PREV_PROS'] = 'url(#prev-pros-grad)';
    color['PROS_PROT'] = 'url(#pros-prot-grad)';
    color['ALL'] = 'url(#all-grad)';

    function initialize() {
        d3.json('/partner-map/', function(error, graph) {
            force
                .nodes(graph.nodes)
                .links(graph.links)
                .start();

            var link = svg.selectAll('.link')
                .data(graph.links)
                .enter().append('line')
                .attr('class', 'link')
                .style('stroke', '#999')
                .style('stroke-opacity', 6)
                .style('stroke-width', 2);

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

            node.append('svg:circle').attr('r', 15)
                .style('stroke', '#fff')
                .style('stroke-width', '1.5px')
                .style('fill', function(d) { return map_types_to_color(d.types, graph.threeps) })
                .style('fill-opacity', 0.5)
                .on('mouseenter', function(e) { $(this).css('fill-opacity', 1.0) })
                .on('mouseleave', function(e) { $(this).css('fill-opacity', 0.5) });

            var legend = svg.append("g")
                .attr("class", "legend")
                .attr("transform", "translate(50,30)")
                .style("font-size", "12px")
                .call(createLegend, {
                    "Prevention": {
                        color: color.PREVENTION
                    },
                    "Protection": {
                        color: color.PROTECTION
                    },
                    "Prosecution": {
                        color: color.PROSECUTION
                    }
                });

            $('.partner-map-svg').bind('DOMMouseScroll mousewheel', function(e) {
                e.preventDefault();
                var curRad = parseInt($('.node circle').attr('r'), 10);
                var curCharge = force.charge();
                if(e.originalEvent.wheelDelta > 0) {
                    $('.node circle').attr('r', ++curRad);
                    force.charge(curCharge - 500).start();
                } else {
                    if (curRad > 1 && curCharge + 500 < 0) {
                        $('.node circle').attr('r', --curRad);
                        force.charge(curCharge + 500).start();
                    }
                }
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
        });
    }

    function createLegend(g, items) {
        g.each(function() {
            var g= d3.select(this),
                svg = d3.select(g.property("nearestViewportElement")),
                legendPadding = g.attr("data-style-padding") || 5,
                lb = g.selectAll(".legend-box").data([true]),
                li = g.selectAll(".legend-items").data([true])

            lb.enter().append("rect").classed("legend-box",true).attr('fill', 'white').attr('stroke', 'black')
            li.enter().append("g").classed("legend-items",true)

            items = d3.entries(items).sort(function(a,b) { return a.value.pos-b.value.pos})

            li.selectAll("text")
                .data(items,function(d) { return d.key})
                .call(function(d) { d.enter().append("text")})
                .call(function(d) { d.exit().remove()})
                .attr("y",function(d,i) { return i+"em"})
                .attr("x","1em")
                .text(function(d) { ;return d.key})

            li.selectAll("circle")
                .data(items,function(d) { return d.key})
                .call(function(d) { d.enter().append("circle")})
                .call(function(d) { d.exit().remove()})
                .attr("cy",function(d,i) { return i-0.25+"em"})
                .attr("cx",0)
                .attr("r","0.4em")
                .style("fill",function(d) { console.log(d.value.color);return d.value.color})

            // Reposition and resize the box
            var lbbox = li[0][0].getBBox()
            lb.attr("x",(lbbox.x-legendPadding))
                .attr("y",(lbbox.y-legendPadding))
                .attr("height",(lbbox.height+2*legendPadding))
                .attr("width",(lbbox.width+2*legendPadding))
      })
      return g
    }

    function create_popover_content(node) {
        return "<h4>" + node.name + "</h4>" + (node.addr ? "<i>" + node.addr + "</i>" : "");
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
        $.each(types, function(index, type) {
            if (type == three_ps.PROTECTION)
                has_prot = true;
            if (type == three_ps.PROSECUTION)
                has_pros = true;
            if (type == three_ps.PREVENTION)
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

    return { initialize: initialize };
});
