//$('#stuTrajectoryModal').on('show.bs.modal', function (event) {
$('.trajectoryBtn').click(function (event) {
  //var button = $(event.relatedTarget) // Button that triggered the modal
  //var button = $(this); // Button that triggered the modal

  // Extract info from data-* attributes
  var stuid = $(this).data('stuid')
  var firstname = $(this).data('firstname')

  // Remove existing canvas
  $("#graphCanvas").empty();

  // Erase class management fields
  $("#divUpdateClass").empty();


  // Get the competencies for current user
  $.ajax({
    type: "POST",
    url: "/assessment/stats_json",
    data: JSON.stringify({userid: stuid}),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(result){
      draw_trajectory_in_canvas(result);
      console.log("Drawing graph");
    },
    failure: function(err){
      console.log("Ajax call failed!", err)
    }
    
  });

  $("#graphCanvas").append("<div>Trajectory for <strong>" + firstname + "</strong></div>");

})


function draw_trajectory_in_canvas(graph){
      var width = 600;
      var height = 300;

      //radius of each node
      var node_r = 25;

      // Rescale the node position values.
      // If the nodes are towards the edges, push them in.
      graph.nodes.forEach(function(d){
        if (d.x_ <= 0.2){
            d.x_ = d.x_ * width + node_r;
        }
        else if (d.x_ >= 0.8){
            d.x_ = d.x_ * width - node_r;
        }
        else{
            d.x_ = d.x_ * width;
        }

        if (d.y_ <= 0.2){
            d.y_ = d.y_ * height + node_r;
        }
        else if (d.y_ >= 0.8){
            d.y_ = d.y_ * height - node_r;
        }
        else{
            d.y_ = d.y_ * height;
        }
      });

      console.log(graph.nodes);

      var arrowWidth = 8;

      // Bootstrap row to contain svg and node info card
      var btsrp_row = d3.select("#graphCanvas")
            .append("div")
            .attr("class", "container")
            .append("div")
            .attr("class", "row")

      var svg = btsrp_row.append("div")
            .attr("class", "col-sm-8")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            //.attr("viewBox", "0 0 " + width.toString() + " " + height.toString())
            .attr("overflow", "scroll")

      // Container for competency node information
      var info_cntr = btsrp_row.append("div")
            .attr("class", "col-sm-4")
            .append("div")
            .attr("id", "competencyInfoContainer")

      var rectRound = 6;
      var div_tip = d3.select("body").append("div")
         .attr("class", "tooltip")
         .style("opacity", 0);

      // Create the svg:defs element and the main gradient definition.
      var svgDefs = svg.append('svg:defs');

      // build the arrow.
      svgDefs.selectAll("marker")
        .data(["arrow"])                   // Different link/path types can be defined here
        .enter().append("marker")    // This section adds in the arrows
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 10)
        .attr("refY", 0.0)
        .attr("markerWidth", 5)
        .attr("markerHeight", 5)
        .attr("orient", "auto")
        .attr("fill", "#aaa")
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");

      // Apply color gradient
      var bgrGradient = svgDefs.append("linearGradient");
      bgrGradient.attr("id", "bgrGradient")

      // Since there are three Grades (6, 7, 8), we add 4 stops
      bgrGradient.append("stop")
        .attr("offset", "33%")
        .attr("stop-color", "white")
      bgrGradient.append("stop")
        .attr("offset", "33%")
        .attr("stop-color", "#FF6")
      bgrGradient.append("stop")
        .attr("offset", "66%")
        .attr("stop-color", "#FF6")
      bgrGradient.append("stop")
        .attr("offset", "66%")
        .attr("stop-color", "#F60")

      // Place a rectangle over the canvas
      //var svgRect = svg.append("rect")
      //      .attr("width", width)
      //      .attr("height", height)
      //      .style("fill", "url(#linearGradient)")

      var linkG = svg.append("g");
      var nodeG = svg.append("g");

      // Function which draws the graph data
      function render(graph){


        /*
          Replace line with path:
          https://stackoverflow.com/a/41229068
        */
        var all_links = linkG.selectAll("path").data(graph.links);
        var linkEnter = all_links.enter().append("path")
          .attr("class", "link-line")
          .attr("stroke-width", 2)
          .attr("stroke", "#aaa")
          .attr("fill", "none")
          .attr("cursor", "pointer")
          .attr("marker-end", "url(#arrow)")
          .attr("d", function(d){
            var dx = d.target.x_ - d.source.x_;
            var dy = d.target.y_ - d.source.y_;
            var dr = Math.sqrt(dx * dx + dy * dy);

            console.log(dr);

            return "M" + d.source.x_ + "," + d.source.y_ + "A" + dr + "," + dr + " 0 0,1 " + d.target.x_ + "," + d.target.y_;
          })
          .on("mouseover", function(d, i){
            // color the edge
            var lnk = d3.select(this);
            lnk.attr("stroke", "orange")
                .attr("stroke-width", 3)

            // color the source and target nodes
            d3.select("#nd" + d.source.id.replace(/\./g, ""))
              .attr("stroke-width", 3)
              .attr("stroke", "orange");
            d3.select("#nd" + d.target.id.replace(/\./g, ""))
              .attr("stroke-width", 3)
              .attr("stroke", "orange");
          })
          .on("mouseout", function(d, i){
            // revert the edge color
            var lnk = d3.select(this);
            lnk.attr("stroke", "#aaa")
                .attr("stroke-width", 2)

            // revert the colors of source and target
            d3.select("#nd" + d.source.id.replace(/\./g, ""))
              .attr("stroke-width", 1)
              .attr("stroke", "#ff8fff");
            d3.select("#nd" + d.target.id.replace(/\./g, ""))
              .attr("stroke-width", 1)
              .attr("stroke", "#ff8fff");
          });

        linkEnter.attr("d", function(d){
            var pl = this.getTotalLength();

            // radius of circle plus marker head
            //var r = d3.select("#nd" + d.target.id.replace(/\./g, "")).attr("r");
            var r = node_r;

            // position close to where path intercepts circle
            var m = this.getPointAtLength(pl - r);

            var dx = m.x - d.source.x_,
              dy = m.y - d.source.y_,
              dr = Math.sqrt(dx * dx + dy * dy);

            return "M" + d.source.x_ + "," + d.source.y_ + "A" + dr + "," + dr + " 0 0,1 " + m.x + "," + m.y;
          });

          /*
          .attr("x1", function(d) { return d.source.x_ * width; })
          .attr("y1", function(d) { return d.source.y_ * height; })
          .attr("x2", function(d) { return d.target.x_ * width + node_r * Math.sign(d.target.x_ - d.source.x_);; })
          .attr("y2", function(d) { return d.target.y_ * height + node_r * Math.sign(d.target.y_ - d.source.y_);; })
          */

        all_links.exit().remove();
        all_links = all_links.merge(linkEnter);
        
        var node = nodeG.selectAll("g").data(graph.nodes);
        var nodeEnter = node.enter().append("g");
        node.exit().remove();

        nodeEnter.append("circle")
          .attr("class", "node-circle")
          .attr("id", function (d){ return "nd" + d.id.replace(/\./g, ""); })  // . is not allowed in id
          .attr("cx", function (d){ return d.x_; })
          .attr("cy", function (d){ return d.y_; })
          .attr("r", function (d){
            if (d.game_levels.length == 0){
              return 2;
            }
            else{
              return node_r;
            }
          })
          .attr("cursor", "pointer")
          .attr("fill", function (d){
            var color = "#90ee90";
            if (d.competency != 1){
              color = "#fff";
            }
            return color;
          })
          .attr("stroke", "#ff8fff")
          .attr("stroke-width", 1)
          .on("click", showNodeDetails)

        nodeEnter.append("text")
          .attr("class", "node-text")
          .attr("text-anchor", "middle")
          .attr("font-size", "15px")
          .attr("cursor", "pointer")
          .text(function (d){ 
            if (d.game_levels.length == 0){
              return " ";
            }
            else{
              return d.id;
            }
          })
          .attr("x", function (d){ return d.x_ - node_r / 8; })
          .attr("y", function (d){ return d.y_; })
          .on("click", showNodeDetails)

        node = node.merge(nodeEnter);

        // Handle color changes on the nodes
        node.select(".node-circle")
          .on("mouseover", function(d, i){
            d3.select(this)
              .attr("stroke-width", 3)
              .attr("stroke", "orange");

            //showNodeDetails(d, i);
          })
          .on("mouseout", function(d, i){
            d3.select(this)
              .attr("stroke-width", 1)
              .attr("stroke", "#ff8fff");

            //showNodeDetails(d, i);
          })

        // Same effect should apply for text on each node.
        node.select(".node-text")
          .on("mouseover", function(d, i){
            d3.select(this.previousElementSibling)
              .attr("stroke-width", 3)
              .attr("stroke", "orange");
          })
          .on("mouseout", function(d, i){
            d3.select(this.previousElementSibling)
              .attr("stroke-width", 1)
              .attr("stroke", "#ff8fff");
          })


      }  // End render() def.
        
      graph.links = graph.links.map(function (d){
        d.source = graph.nodes[d.source];
        d.target = graph.nodes[d.target];
        return d;
      });

      render(graph);


  function showNodeDetails(d, i){
    // Display details about the node in a box.
    //console.log(d.summary);

    // First, remove any existing box
    var prev = d3.select("#competencyInfo");

    if (!prev.empty()){
      // If it's the same element, remove and do nothing
      var prev_id = prev.select("div").attr("id");
      prev.remove();

      if ("info_" + d.id === prev_id){
        return;
      }
    }

    // Create a new one
    var main_info_div = d3.select("#competencyInfoContainer").append("div")
      .attr("id", "competencyInfo")

    var info_div = main_info_div.append("div")
      .attr("id", "info_" + d.id)
      .attr("class", "card bg-light")

    var info_div_header = info_div.append("div")
      .attr("class", "card-header")

    var info_div_body = info_div.append("div")
      .attr("class", "card-body")

    info_div_header.append("h6")
      .text("Competency: " + d.id)

    info_div_body.append("p")
      .attr("class", "card-text scrollClass")
      .text(d.summary)

    var list_group = info_div_body.append("ul")
      .attr("class", "list-group list-group-flush scrollClass")

    list_group.selectAll("li")
      .data(d.game_levels)
      .enter()
      .append("li")
      .attr("class", "list-group-item")
      .text(function (obj){ return obj; })

    return;

  }  // End showNodeDetails() def.

}
