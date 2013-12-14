var fill = d3.scale.category20();

function draw(words) {
	d3.select("#word-cloud").append("svg")
    .attr("width", 800)
    .attr("height", 400)
  	.append("g")
    .attr("transform", "translate(400,200)")
  	.selectAll("text")
    .data(words)
  	.enter().append("text")
    .style("font-size", function(d) { return d.size + "px"; })
    .style("font-family", "Impact")
    .style("fill", function(d, i) { return fill(i); })
    .attr("text-anchor", "middle")
    .attr("transform", function(d) {
      return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
    })
    .text(function(d) { return d.text; });
}

var data = {
	'org_id': document.URL.split("/")[4]
}

$.get('/get_org_keywords/', data)
	.done(function(result){
		if(!Object.keys(result).length) {
			$('#no-keywords').show();
			return;
		}

		d3.layout.cloud().size([800, 400])
		.words(Object.keys(result).map(function(d) {
		return {text: d, size: 10 + result[d]/3};
	}))
    .padding(5)
    .rotate(0)
    .fontSize(function(d) { return d.size; })
    .on("end", draw)
    .start();
}).fail(function(result){
	$('#no-keywords').show();
});
