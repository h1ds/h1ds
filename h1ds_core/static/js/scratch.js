////////////////////////////////////////////////////////////////////////
//// Various chunks of js not currenly in use, but may be useful again later.
////////////////////////////////////////////////////////////////////////


////////////
// tree from http://bl.ocks.org/mbostock/raw/1093025/

var w = $("#test-nav").width();

var h = 800,
    i = 0,
    barHeight = 20,
    barWidth = w * .8,
    duration = 400,
    root;

var tree = d3.layout.tree()
    .size([h, 100]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

//var vis = d3.select("#test-nav").append("svg:svg")
 //   .attr("width", w)
 //   .attr("height", h)
 // .append("svg:g")
 //   .attr("transform", "translate(20,30)");


function updateNav(source) {

  // Compute the flattened node list. TODO use d3.layout.hierarchy.
  var nodes = tree.nodes(root);
  
  // Compute the "layout".
  nodes.forEach(function(n, i) {
    n.x = i * barHeight;
  });
  
  // Update the nodes…
  var node = vis.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });
  
  var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .style("opacity", 1e-6);

  // Enter any new nodes at the parent's previous position.
  nodeEnter.append("svg:rect")
      .attr("y", -barHeight / 2)
      .attr("height", barHeight)
      .attr("width", barWidth)
      .style("fill", color)
      .on("click", click);
  
  nodeEnter.append("svg:text")
      .attr("dy", 3.5)
      .attr("dx", 5.5)
      .text(function(d) { return d.name; });
  
  // Transition nodes to their new position.
  nodeEnter.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
      .style("opacity", 1);
  
  node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
      .style("opacity", 1)
    .select("rect")
      .style("fill", color);
  
  // Transition exiting nodes to the parent's new position.
  node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .style("opacity", 1e-6)
      .remove();
  
  // Update the links…
  //var link = vis.selectAll("path.link")
   //   .data(tree.links(nodes), function(d) { return d.target.id; });
  
  // Enter any new links at the parent's previous position.
  //link.enter().insert("svg:path", "g")
   //   .attr("class", "link")
    //  .attr("d", function(d) {
  //      var o = {x: source.x0, y: source.y0};
  //      return diagonal({source: o, target: o});
  //    })
  //  .transition()
  //    .duration(duration)
  //    .attr("d", diagonal);
  
  // Transition links to their new position.
  //link.transition()
  //    .duration(duration)
  //    .attr("d", diagonal);
  
  // Transition exiting nodes to the parent's new position.
  //link.exit().transition()
  //    .duration(duration)
  //    .attr("d", function(d) {
  //      var o = {x: source.x, y: source.y};
  //      return diagonal({source: o, target: o});
  //    })
  //    .remove();
  
  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  updateNav(d);
}


function color(d) {
  return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
}

var isOdd = function(someNumber){
    return (someNumber%2 == 0) ? false : true;
};

function updateEvents() {
 $.getJSON('/dashboard/', function(data){
  $.each(data, function(eventID) {
   var topRowId=parseInt($(".event-id").eq(1).text());
   if (parseInt(data[eventID].pk) > topRowId) {
    $("tr").eq(0).after('<tr><td class="event-id">'+data[eventID].pk+'</td><td class="name">'+data[eventID].fields.signal+'</td><td class="time">'+data[eventID].fields.time+'</td></tr>');
    $("tr").eq(1).effect("highlight", {color:"#ff6600"}, 300000);
   } // end if
  }); // end each
 }); // end getJSON
} // end function

function autoUpdateEvents() {
    setInterval(updateEvents, 2000);
}


// HACK
updateShotNav = function() {
    var current_url = new H1DSUri(window.location.toString());
    var current_shot = current_url.getShot();
    if (current_shot === 0) {

	current_url.uri_components.path = $("#debug-node-path").html();
	current_shot = current_url.getShot();
	//current_shot = Number($("#h1ds-shot-current").html());
	//console.log($("#h1ds-shot-current").html());
	//var tmp_path = current_url.uri_components.path;
	//if (tmp_path[tmp_path.length-1] === "/"){
	//    
	//} else {
	//    current_url.uri_components.path = current_url.uri_components.path+"/"+current_shot;
//	}
    }
    current_url.setShot(current_shot+1);
    var next_url = current_url.renderUri();
    current_url.setShot(current_shot-1);
    var previous_url = current_url.renderUri();
    $("#h1ds-shot-previous").html("<a class='shotnav' href='"+previous_url+"'>&larr;</a>");
    $("#h1ds-shot-next").html("<a class='shotnav' href='"+next_url+"'>&rarr;</a>");
	//.attr("method", "get")
	//.attr("action", previous_url);
    //$("#h1ds-shot-previous form input[type=hidden]").remove();
}


function plotSignal2D() {
    // custom image manipulation for data
    var container  = $("#dummy");
    var query_char = window.location.search.length ? '&' : '?';
    var image_query = window.location.search + query_char + 'format=json';

    $.getJSON(image_query, dataReady);

    function dataReady(signal_data) {
	var canvas = document.createElement("canvas");
	canvas.width = signal_data.dim[0].length;
	canvas.height = signal_data.dim[1].length;
	container.height(canvas.height);
	var context = canvas.getContext('2d');
	var imageData = context.getImageData(0,0,canvas.width, canvas.height);

	for (var x = 0; x < imageData.width; x++) {
	    for (var y = 0; y < imageData.height; y++) {
		var index = 4 * (y * imageData.width + x);
		var imval = 255*(signal_data.data[x][y] - signal_data.min)/(signal_data.max-signal_data.min);
		imageData.data[index] = imval;
		imageData.data[index + 1] = imval;
		imageData.data[index + 2] = imval;
		imageData.data[index + 3] = 255;
	    }
	}
	context.putImageData(imageData, 0, 0);
	container.append(canvas);
    } // end: dataReady
}

