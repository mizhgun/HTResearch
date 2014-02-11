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
        .style("font-size", function (d) {
            return d.size + "px";
        })
        .style("font-family", "Impact")
        .style("fill", function (d, i) {
            return fill(i);
        })
        .attr("text-anchor", "middle")
        .attr("transform", function (d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function (d) {
            return d.text;
        });
}

var data = {
    'org_id': document.URL.split("/")[4]
}

$.get('/get-org-keywords/', data)
    .done(function (result) {
        if(result) {
            var coeff = 0.15;
            d3.layout.cloud().size([800, 400])
                .words(result.map(function (d, i) {
                    console.log(d);
                    return {text: d, size: 10 + 100 * Math.pow(Math.E, -coeff*i)};
                }))
                .padding(5)
                .rotate(0)
                .fontSize(function(d) {
                    return d.size;
                })
                .on("end", draw)
                .start();
        } else {
            $('#no-keywords').show();
        }
    }).fail(function(result) {
        $('#no-keywords').show();
    });
