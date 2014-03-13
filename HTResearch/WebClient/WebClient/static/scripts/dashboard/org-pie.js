function organizationBreakdown(element) {
    element = element || 'body';

    var w = 300,                        //width
        h = 300,                            //height
        r = 100,                            //radius
        color = d3.scale.category20c();     //builtin range of colors

    data = [{"label":"one", "value":20},
        {"label":"two", "value":50},
        {"label":"three", "value":30}];

    var vis = d3.select(element)
        .append("svg:svg")
        .data([data])
        .attr("width", w)
        .attr("height", h)
        .append("svg:g")
        .attr("transform", "translate(" + r + "," + r + ")")

    var arc = d3.svg.arc()
        .outerRadius(r);

    var pie = d3.layout.pie()
        .value(function(d) { return d.value; });

    var arcs = vis.selectAll("g.slice")
        .data(pie)
        .enter()
        .append("svg:g")
        .attr("class", "slice");

    arcs.append("svg:path")
        .attr("fill", function(d, i) { return color(i); } )
        .attr("d", arc);

    arcs.append("svg:text")
        .attr("transform", function(d) {
            d.innerRadius = 0;
            d.outerRadius = r;
            return "translate(" + arc.centroid(d) + ")";
        })
        .attr("text-anchor", "middle")
        .text(function(d, i) { return data[i].label; });

}