(function() {

	var margin = {top: 20, right: 20, bottom: 30, left: 40},
	    width = 960 - margin.left - margin.right,
	    height = 700 - margin.top - margin.bottom;

	var DrawBarChart;
	var x = d3.scale.linear()
			.range([0, height]);

	var y = d3.scale.linear()
	    .range([height, 0]);

	var svg = d3.select("#barChart").append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	DrawBarChart = function(error, response) {
		sessionStorage.setItem("conceptFrequency", JSON.stringify(response.results));
		var data = response.results;
		var ordering = response.concept_order;

		data.sort(function(a, b) {
			if($.inArray(b.concept, ordering) === -1) return 1
			if($.inArray(a.concept, ordering) === -1) return -1
			return ordering.indexOf(a.concept) - ordering.indexOf(b.concept);
		});

		if(error) throw error;
		    // .rangeRoundBands([0, 35*data.length], .1);
		x.domain([0, data.length]);

	    var xAxis = d3.svg.axis()
	        .scale(x)
	        .orient("left")
	        .tickSize(2)
			.tickFormat(function(d,i){ return data[i].concept; })
			.tickValues(d3.range(data.length));

		// x.domain(data.map(function(d) { return d.concept; }));
		y.domain([0, d3.max(data, function(d) { return d.frequency; })]);

		var bars = svg.selectAll(".bars")
		      .data(data)
		    .enter().append("g")
		      .attr("class", "bars")
		      .attr("transform", function(d, i) { return "translate(0," + i * 35 + ")"; });

		bars.append("rect")
		    .attr("class", "bar")
		    .attr("transform", "translate("+130+",0)")
		    .attr("height", 30)
		    .attr("width", function(d) { return x(d.frequency - (d.frequency/2)); })
		
		bars.append("text")
		    .attr("x", 100)
		    .attr("dy", (30/1.5) + "px")
		    .style("fill", "#000")
		    .style("text-anchor", "end")
		    .text(function(d) {return d.concept});

		bars.append("text")
		    .attr("x", function(d) { return x(d.frequency - (d.frequency/2)) + 125; })
		    .attr("dy", (30/1.5) + "px")
		    .style("fill", "#FFF")
		    .style("text-anchor", "end")
		    .text(function(d) {return d.frequency});	
	};

	var args = location.pathname.split("/");
	var params = "?term="+args[1]+"&year="+args[2]+"&classe="+args[3]+"&test="+args[4];
	d3.json("/concepts_bar"+params, DrawBarChart);
})();
