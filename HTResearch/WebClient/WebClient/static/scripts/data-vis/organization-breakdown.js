var pie = d3.layout.pie().value(function(d) {
    return d.a;
});

var color = d3.scale.category20();
var arrayRange = 100;
var width = 100;
var height = 100;

function fillArray() {
    return {
        port: "port",
        octetTotalCount: Math.ceil(Math.random()*(arrayRange))
    };
}

var vis = d3.select('#pie-chart').append('svg:svg')
    .attr('width', w)
    .attr('height', h);

var totalUnits = centerGroup.append('svg:text')
    .attr('class', 'units')
    .attr('dy', 21)
    .attr('text-anchor', 'middle')
    .text('kb');

function update() {
    arraySize = Math.ceil(Math.random() * 10);
    streakerDataAdded = d3.range(arraySize).map(fillArray);

    // DRAW ARC PATHS
    paths = arc_group.selectAll('path').data(filteredPieData);
    paths.enter().append('svg:path')
        .attr('stroke', 'white')
        .attr('stroke-width', 0.5)
        .attr('fill', function(d, i) { return color(i); })
        .transition()
            .duration(tweenDuration)
            .attrTween('d', pieTween);
    paths
        .transition()
            .duration(tweenDuration)
            .attrTween('d', pieTween);
    paths.exit()
        .transition()
            .duration(tweenDuration)
            .attrTween('d', removePieTween)
        .remove();
}