define(['jquery', 'd3'], function($, d3) {
    var width = window.innerWidth,
        height = window.innerHeight;

    var color = d3.scale.category20();

    var force = d3.layout.force()
        .charge(-10000)
        .gravity(0.7)
        .friction(0.3)
        .linkDistance(30)
        .size([width, height]);

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    function initialize() {
        d3.json("/partner-map/", function(error, graph) {
            force
                .nodes(graph.nodes)
                .links(graph.links)
                .start();

            var link = svg.selectAll(".link")
                .data(graph.links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke", "#999")
                .style("stroke-opacity", 6)
                .style("stroke-width", 2);

            var node = svg.selectAll(".node")
                .data(graph.nodes)
                .enter().append("svg:g")
                .attr("class", "node")
                .attr("transform", function(d) {return "translate(" + d.x + "," + d.y +")"; })
                .call(force.drag);

            node.append("svg:circle").attr("r", 30)
                .style("stroke", "#fff")
                .style("stroke-width", "1.5px")
                .style("fill", color(0))
                .style("fill-opacity", 0.5);

            node.append("svg:text")
                .text(function(d) { return d.name; })
                .style("fill", "#555")
                .style("font-family", "Arial")
                .style("font-size", 12)
                .style("text-anchor", "middle");

            node.append("title")
                .text(function(d) {return d.name; });


            force.on("tick", function() {
                link.attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });

                node.attr("cx", function(d) { return d.x; })
                    .attr("cy", function(d) { return d.y; })
                    .attr("transform", function(d) {return "translate(" + d.x + "," + d.y +")"; });
            });
        });
    }

    return { initialize: initialize };
});
