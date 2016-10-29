document.addEventListener("DOMContentLoaded",
    function (e) {
        function plotGraph(graph) {
            var link = svg.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(graph.links)
                .enter()
                .append("line")
                .attr("stroke-width",
                    function(d) {
                        var v = 2 * Math.log10(d.value * Math.pow(10, -8));
                        if (v < 1) {
                            v = 1;
                        }
                        return v;
                    })
                .style("stroke", function(d) {
                    return d.color;
                });

            var node = svg.append("g")
                .attr("class", "nodes")
                .selectAll("circle")
                .data(graph.nodes)
                .enter()
                .append("circle")
                .attr("r", function(d) {
                    if (d.id === d3.select("#address").text().replace(/\n/g, "").replace(/\r/g, "").replace(/ /g, "")) {
                        return 10;
                    } else {
                        return 5;
                    }
                })
                .attr("fill", function () { return color(Math.floor(Math.random() * 10) + 1); })
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

            node.append("title")
                .text(function (d) { return d.title; });

            simulation
                .nodes(graph.nodes)
                .on("tick", ticked);

            simulation.force("link")
                .links(graph.links);

            function ticked() {

                link
                    .attr("x1", function (d) { return d.source.x; })
                    .attr("y1", function (d) { return d.source.y; })
                    .attr("x2", function (d) { return d.target.x; })
                    .attr("y2", function (d) { return d.target.y; });

                node
                    .attr("cx", function (d) { return d.x; })
                    .attr("cy", function (d) { return d.y; });
            }
        }

        function dragstarted(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d) {
            if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        var svg = d3.select("svg");
        var width = +svg.attr("width");
        var height = +svg.attr("height");

        var color = d3.scaleOrdinal(d3.schemeCategory20);

        var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(function (d) { return d.id; }))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));

        var graphJson = {};

        var graphJsonText = d3.select("#graph-json").text().replace(/\n/g, "").replace(/\r/g, "").replace(/ /g, "");
        if (graphJsonText) {
            graphJson = JSON.parse(graphJsonText);
        }

        if (!(Object.keys(graphJson).length === 0 && graphJson.constructor === Object)) {
            plotGraph(graphJson);
        }

        function clicked() {
            console.log(d3.select(this).select("title").text());
            var title = d3.select(this).select("title").text();
            if (parseInt(title).toString() === title) {
                window.open('https://blockchain.info/tx/' + title);
            } else {
                window.open('https://blockchain.info/address/' + title);
            }
        }

        d3.selectAll("circle").attr("onclick", clicked);

    });

function loadAddress() {
    var address = document.getElementById("request-address").value;
    var max_tx = document.getElementById("max_tx").value;
    var depth_limit = document.getElementById("depth_limit").value;
    var branch_limit = document.getElementById("branch_limit").value;
    window.location = "/" + address + "/" + max_tx + "/" + depth_limit + "/" + branch_limit;
}





