// Custom javascript code for H1 data system
// David Pretty, 2010-2013

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

///////////////////////////////////////////////

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

$('#masonry-container').masonry({
     itemSelector: '.mbox',
     columnWidth: 384
 });


// start: adapted from http://jqueryui.com/demos/sortable/#portlets

$(function() {

    $(".column").each(function(i) {
	var thisColumn = this;
	$(thisColumn).sortable({
	    connectWith: ".column",
	    handle: ".portlet-header",
	    update: function(e,ui) {
		$.cookie("sortorder"+thisColumn.id, 
			 $(thisColumn).sortable("toArray").join(), 
			 {path:'/'});
	    }
	});
	// this breaks input forms in firefox..
	// $(thisColumn).disableSelection();
    });

    $( ".portlet" ).addClass( "ui-widget ui-widget-content ui-helper-clearfix ui-corner-all" )
	.find( ".portlet-header" )
	.addClass( "ui-widget-header ui-corner-all" )
	.prepend( "<span class='ui-icon ui-icon-minusthick'></span>")
	.end()
	.find( ".portlet-content" );

    $( ".portlet-header .ui-icon" ).click(function() {
	$( this ).toggleClass( "ui-icon-minusthick" ).toggleClass( "ui-icon-plusthick" );
	$( this ).parents( ".portlet:first" ).find( ".portlet-content" ).toggle(
	    $.cookie($(this).parents(".portlet:first")[0].id, 
		     $(this).parents(".portlet:first").find(".portlet-content").is(":hidden") ? 'expanded' : 'collapsed', 
		     {path:'/'})
	);
    });

});

// end: adapted from http://jqueryui.com/demos/sortable/#portlets


function loadCookie() {

    // loop through all columns...
    $('.column').each(function(i) {
	var cookieItem = $.cookie("sortorder"+this.id);
	var thisColumn = this;
	if (cookieItem) {
	    $(cookieItem.split(',')).each(function (i, id) {
		$("#"+id).appendTo(thisColumn);
	    });
	}
	$(this).sortable();
    });

    // also load toggle states

    // find all portlet ids...
    $('.portlet').each(function(i) {
	var thisCookie = $.cookie(this.id);
	if (thisCookie) {
	    if (thisCookie === 'collapsed') {
		$( this ).find('.ui-icon').toggleClass( "ui-icon-minusthick" ).toggleClass( "ui-icon-plusthick" );
		$(this).find(".portlet-content").hide();
	    }
	}
    });

    // load latest-shot-tracking state.
    var shotTracking = $.cookie('shotTracking');
    if (shotTracking === 'true') {
	turnOnShotTracker();
    } else {
	turnOffShotTracker();
    }
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


function getPlotWidth(id){
    //
    // args: id selector of container div
    // returns: margins and plot width
    //
    var vis_width = $(id).width();
    //var plot_width = parseInt(0.9*vis_width);
    //var both_margins = vis_width - plot_width;
    //if (isOdd(both_margins)) {
	// plot_width -= 1;
	// both_margins += 1;
    // }
    // var margin = both_margins/2;
    var margin_left = 30;
    var margin_right = 0;
    return {'plot':vis_width-margin_left-margin_right, 'marginLeft':margin_left, 'marginRight':margin_right}
}

function fillPlot(data) {
    // return a line of points from data object
    // require data.dim, data.data=[[min,,,,], [max,,,,]]
    
    var d = Array(2*data.dim.length);

    for( i=0; i < data.dim.length; i++){
        d[i]=[data.dim[i],data.data[0][i]];
        d[data.dim.length + i]=[data.dim[data.dim.length-(i+1)],data.data[1][data.dim.length-(i+1)]];
    }
    return d;
}

// If we have min and max signals, then we fill the area between them.
function isMinMaxPlot(signal_data) {
    return  (($.inArray("min", signal_data.labels) > -1) && 
	     ($.inArray("max", signal_data.labels) > -1) && 
	     (signal_data.labels.length == 2)) ? true : false;
}


/*
 * Interactive data plots.
 * 
 */

/*********************************************************************/
/*********************************************************************/

// an object which allows easy manipulation of query string filters.
function H1DSUri(original_uri) {
    this.uri_components = parseUri(original_uri);
    this.h1ds_filters = {};
    this.non_h1ds_query = {};
    //var filter_re = /^f(\d+)_(name|arg(\d+))$/;
    var filter_re = /^f(\d+)(_(\w+))?/;
    for (var key in this.uri_components.queryKey) {
	if (this.uri_components.queryKey.hasOwnProperty(key)) {
	    var filter_info = filter_re.exec(key);
	    if (filter_info) {
		if (!this.h1ds_filters.hasOwnProperty(filter_info[1])) {
		    this.h1ds_filters[filter_info[1]] = {'name':"", "kwargs":{}};
		}
		if (typeof filter_info[2] === 'undefined') {
		    this.h1ds_filters[filter_info[1]].name = this.uri_components.queryKey[key];
		}
		else {
		    this.h1ds_filters[filter_info[1]].kwargs[filter_info[3]] = this.uri_components.queryKey[key];
		}
	    }
	    else {
		this.non_h1ds_query[key] = this.uri_components.queryKey[key];
	    }
	}
    }
}

H1DSUri.prototype.getNextFilterID = function() {
    var largest_fid = -1;
    for (var key in this.h1ds_filters) {
	if (this.h1ds_filters.hasOwnProperty(key)) {
	    if (Number(key) > largest_fid) largest_fid=Number(key);
	}
    }
    return largest_fid + 1;
};

H1DSUri.prototype.appendFilter = function(filter_name, filter_kwargs) {
    var new_id = this.getNextFilterID();
    this.h1ds_filters[String(new_id)] = {'name':filter_name,'kwargs':filter_kwargs};
};

H1DSUri.prototype.renderUri = function() {
    var newQueryKey = {};
    for (var key in this.non_h1ds_query) {
	if (this.non_h1ds_query.hasOwnProperty(key)) {
	    newQueryKey[key] = this.non_h1ds_query[key];
	}
    }

    for (var key in this.h1ds_filters) {
	if (this.h1ds_filters.hasOwnProperty(key)) {
	    newQueryKey["f"+key] = this.h1ds_filters[key].name;
	   // for (var i=0; i<this.h1ds_filters[key].args.length;i++) { // can 
		// newQueryKey["f"+key+"_arg"+i] = this.h1ds_filters[key].args[i];
	    //}
	    for (var fkey in this.h1ds_filters[key].kwargs) {
		newQueryKey["f"+key+"_"+fkey] = this.h1ds_filters[key].kwargs[fkey];
	    }
	}
    }

    var new_uri_components = jQuery.extend({}, this.uri_components);
    new_uri_components.queryKey = newQueryKey;
    return makeUri(new_uri_components);
};

H1DSUri.prototype.isBinary = function() {
    return (this.non_h1ds_query['format'] === 'bin') 
}



// Functions to modify a URL to return data suitable for a given plot type

function getSpectrogramUri(original_uri) {
    // assume original_url gives a timeseries.
    var h1ds_uri = new H1DSUri(original_uri);
    h1ds_uri.appendFilter('slanted_baseline', {'window':10});
    h1ds_uri.appendFilter('spectrogram', {'bin_size':-1});
    h1ds_uri.appendFilter('norm_dim_range_2d', {'x_min':0, 'x_max':1, 'y_min':0, 'y_max':0.5});
    h1ds_uri.appendFilter('y_axis_energy_limit', {'threshold':0.995});
    h1ds_uri.non_h1ds_query['format'] = 'bin';
    h1ds_uri.non_h1ds_query['bin_assert_dtype'] = 'uint8';
    return h1ds_uri;
}

function getPowerspectrumUri(original_uri, width) {
    // assume original_url gives a timeseries.
    var h1ds_uri = new H1DSUri(original_uri);
    h1ds_uri.appendFilter('slanted_baseline', {'window':10});
    h1ds_uri.appendFilter('power_spectrum', {});
    h1ds_uri.appendFilter('norm_dim_range', {'min':0,'max':0.5});
    //h1ds_uri.appendFilter('x_axis_energy_limit',{'threshold':0.995});
    h1ds_uri.appendFilter('resample_minmax', {'n_bins':width});
    h1ds_uri.non_h1ds_query['format'] = 'json';
    return h1ds_uri;
}

function getRawUri(original_uri, width) {
    // assume original_url gives a timeseries.
    var h1ds_uri = new H1DSUri(original_uri);
    h1ds_uri.appendFilter('resample_minmax', {'n_bins':width});
    h1ds_uri.non_h1ds_query['format'] = 'json';
    return h1ds_uri;
}


/*
 * planned API:
 * var pc = new PlotContainer("#signal-1d-placeholder", [row_1, row_2,..], [col_1, col_2,..]);
 * col_1, col_2 numbers which are normalised to width of container
 * e.g. col_1 -> col_1/(coil_1+col_2) * container_width
 * row_i normalised row heights (height set min of to golden ratio and 90% browser height)
 * 
 * pc.setPlotType(plot number, plot type)
 * pc.addData(dataid, url)
 * pc.addDataToPlot(dataid, plot number)
 * pc.linkAxes([plot number, axis or selection], [plot number, axis or selection])
 *
 * pc.removeDataFromPlot(dataid, plot number)
 * pc.moveData(dataid, from plot, to plot)
 *
 */

function PlotContainer(id, rows, columns) {
    // Store element ID selector
    this.id = id;

    // "raw" should plot any unaltered data? not just line?
    // TODO: js has first class functions - shouldn't we just pass functions around and inspect?
    this.plotTypes = {
	'raw':this.plotLine, 
	'spectrogram':this.plotSpectrogram,
	//'powerspectrum':this.plotPowerSpectrum,
	'powerspectrum':this.plotLine,
	//'raw2d':this.plotRaw2D,
	// TODO - plotSpectrogram just plots 2d? - rename
	// spectrogram stuff is really in the getSpectrogramUri
	'raw2d':this.plotSpectrogram
    }

    // create SVG
    var w = $(id).width();
    // TODO: allow more flexibiity with height - e.g. user resize portlet
    var _h = w/1.618;
    // but don't make it more than 90% of browser height..
    var h = d3.min([_h, 0.9*$(window).height()])
    
    this.svg = d3.select(id)
	.append("svg:svg")
	.attr("width", w)
	.attr("height", h);

    // TODO: replace with algorithm to generate distinct colours.
    this.data_colours = ['#A11D20', '#662C91', '#1859A9', '#008C47', '#ED2D2E', '#010101'];

    this.plotGrid = this.setPlotGrid(rows, columns);
    //this.plotRenderOrder = [];
    //for (var i=0; i<this.plotGrid.length;i++) this.plotRenderOrder[i]=i;

    // url_cache is an object for storing url:plot_data key/value pairs
    // This is the one place where data is stored.
    this.url_cache = {};

    // mapping of data_ids to URLs, colour, etc
    this.data_ids = {}

    // how much to extend the y-axis past the data limits.
    this.dataPadding = 0.05

    // TODO: can we base this on font size rather than magic number of pixels?
    // padding for axes
    this.xAxisPadding = 40;
    this.yAxisPadding = 60;
}


PlotContainer.prototype.plotLine = function(selection) {

    var do_flip = selection.datum().plot.flip;

    selection.append("path")
	.classed("path-filled", function(d) { return d.data.is_minmax })
	.style("stroke", function(d,i) { return d.data.colour; })
	.style("fill", function(d,i) { return d.data.colour; })
	.attr("d", function(d,i) {
	    if (d.data.is_minmax) {
		var fill_data = fillPlot(d.data);
		var line = d3.svg.line()
		    .x(function(a) { return d.plot.x(a[do_flip?1:0]); })
		    .y(function(a) { return d.plot.y(a[do_flip?0:1]); });
		return line(fill_data);
	    } else {
		var line = d3.svg.line()
		    .x(function(a,j) { return d.plot.x(do_flip?a:d.data.dim[j]); })
		    .y(function(a,j) { return d.plot.y(do_flip?d.data.dim[j]:a); });
		return line(d.data.data);
	    }
	});
};

PlotContainer.prototype.plotRaw2D = function(selection) {

}

PlotContainer.prototype.plotSpectrogram = function(selection) {
    // Assume array w/ rects w/ same height and width
    var rect_data = [];
    var cscale=d3.scale.linear().domain([0,1]).range(["blue","red"]);
    var ascale=d3.scale.linear().domain([0,1]).range([0,1]);
    var max_value = 0;
    data = selection.datum();
    var rect_width = data.plot.x(data.data.dim[0][1]) - data.plot.x(data.data.dim[0][0]);
    var rect_height = data.plot.y(data.data.dim[1][0]) - data.plot.y(data.data.dim[1][1]);
    var x_0 = data.plot.x(data.data.dim[0][0]);
    var y_0 = data.plot.y(data.data.dim[1][0]);
    // TODO: last column... 
    for (var x_i = 0; x_i<data.data.dim[0].length-1; x_i++) {
	for (var y_i = 0; y_i<data.data.dim[1].length-1; y_i++) {
	    if (data.data.data[x_i][y_i] > 0) {
		rect_data.push({'xi':x_i, 'yi':y_i});
		if (data.data.data[x_i][y_i] > max_value) max_value = data.data.data[x_i][y_i];
	    }
	}
    }
    var rects = selection.selectAll("rect").data(rect_data);
    rects.enter().append("rect")
	//.attr("x", function(d,i) {return data.plot.x(d.x1)})
	.attr("x", function(d,i) {return x_0+d.xi*rect_width})
	//.attr("y", function(d,i) {return data.plot.y(d.y1)})
	.attr("y", function(d,i) {return y_0-d.yi*rect_height})
	//.attr("width", function(d,i) {return data.plot.x(d.x2)-data.plot.x(d.x1)})
	//.attr("height", function(d,i) {return data.plot.y(d.y1)-data.plot.y(d.y2)})
	.attr("width", rect_width)
	.attr("height", rect_height)
	//.style("fill", function(d,i) {return cscale(d.value/max_value)})
	.style("fill", function(d,i) {return data.data.colour})
	//.style("fill-opacity", function(d,i) {return d.value/max_value});
	.style("fill-opacity", function(d,i) {return data.data.data[d.xi][d.yi]/max_value});
    
};

PlotContainer.prototype.plotPowerSpectrum = function(selection) {
        
};

// In order to allow sharing axes, we make sure the primary axis is
// rendered first, before another plot links to its axis.
// TODO: it might be better to decouple axes from plots to avoid the problem
// of determining render order (with potential for infinite recursion).
//PlotContainer.prototype.updateRenderOrder = function() {
//    var new_order = [];
//    //for (var i=0; i<this.plotRenderOrder.length; i++) {
//    //
//    //}
//    
//};

// New properties is an object whose properties will be added to the plotGrid data
PlotContainer.prototype.setPlot = function(plot_id, new_properties, update) {
    update = typeof update !== 'undefined' ? update : false;

    for (var attrname in new_properties) { 
	this.plotGrid[plot_id][attrname] = new_properties[attrname]; 
    }

    // update render order in case we've changed axis binding.
    //this.updateRenderOrder();


    if (update) {
	this.updateDisplay();
    }
    
};

PlotContainer.prototype.setPlotGrid = function(rows, columns) {
    // convert rows, columns from relative widths to absolute pixel widths
    var column_sum = d3.sum(columns);
    var row_sum = d3.sum(rows);
    var column_pixels = [];
    var row_pixels = [];
    var svg_width = this.svg.attr("width");
    var svg_height = this.svg.attr("height");

    for (var i=0; i<columns.length; i++) {
	column_pixels[i] = svg_width*columns[i]/column_sum;
    }

    for (var i=0; i<rows.length; i++) {
	row_pixels[i] = svg_height*rows[i]/row_sum;
    }

    var plot_grid = [];
    var plot_id_counter = 0;
    var row_translate = 0;
    var col_translate = 0;
    for (var row_i=0; row_i<rows.length; row_i++) {
	col_translate = 0;
	for (var col_i=0;col_i<column_pixels.length;col_i++) {
	    plot_grid[plot_id_counter] = {
		'translate':[col_translate, row_translate], 
		'width':column_pixels[col_i], 
		'height':row_pixels[row_i],
		'data_ids':[],
		'data':[],
		'plotType':"",
		'flip':false,
		'bindAxis':[-1,-1]
	    };
	    col_translate += column_pixels[col_i];
	    plot_id_counter++;	    
	} // end col_i
	row_translate += row_pixels[row_i];
    } // end row_i

    this.svg.attr("height",row_translate);
    $(this.id).height(row_translate);

    return plot_grid;
};

PlotContainer.prototype.addData = function(data_id, data_url) {
    this.data_ids[data_id] = {'uri':data_url, 'colour':this.data_colours.pop()};
};


PlotContainer.prototype.addDataToPlot = function(data_id, plot_id, update) {
    update = typeof update !== 'undefined' ? update : true;

    this.plotGrid[plot_id].data_ids.push(data_id);

    if (update) {
	this.updateDisplay();
    }
};

ProcessH1DSHeaders = function(header_string) {
    var lines = header_string.split("\n");
    var processed_headers = {};
    for (var header_i=0;header_i<lines.length;header_i++) {
	// split the keys and values
	var header_kv = lines[header_i].split(":");
	if (header_kv.length === 2) { // so we can ignore trailing \n
	    if (header_kv[0].match("^X-H1DS")) {
		processed_headers[header_kv[0]] = $.trim(header_kv[1]);
	    }
	}
    }
    return processed_headers;
}

ProcessBinaryData = function(data_string, headers) {
    // TODO: only works with uint8 for now...
    var bin_data = new Uint8Array(str2ab(data_string));    
    var ndim = parseInt(headers["X-H1DS-ndim"]);
    var counter = 0;
    var output = {'data':[], 'dim':[], 'n_dim':ndim};
    // populate dim
    for (var dim=0; dim<ndim; dim++) {
	output['dim'][dim] = [];
	var dim_length = parseInt(headers["X-H1DS-dim-"+dim+"-length"]);
	var dim_delta = parseFloat(headers["X-H1DS-dim-"+dim+"-delta"]);
	var dim_first = parseFloat(headers["X-H1DS-dim-"+dim+"-first"]);	
	for (var i=0; i<dim_length; i++) {
	    output['dim'][dim][i] = dim_delta*i+dim_first;
	}
    }
    // populate data
    // TODO: use a recursion to populate arbitary ndim. 
    var data_delta = parseFloat(headers["X-H1DS-data-delta"]);
    var data_min = parseFloat(headers["X-H1DS-data-min"]);	

    if (ndim > 0) {
	var dim_0_length = parseInt(headers["X-H1DS-dim-0-length"]);
	var dim_0_delta = parseFloat(headers["X-H1DS-dim-0-delta"]);
	var dim_0_first = parseFloat(headers["X-H1DS-dim-0-first"]);	
	for (var i0=0; i0<dim_0_length; i0++){
	    if (ndim > 1) {
		output['data'][i0] = [];
		var dim_1_length = parseInt(headers["X-H1DS-dim-1-length"]);
		var dim_1_delta = parseFloat(headers["X-H1DS-dim-1-delta"]);
		var dim_1_first = parseFloat(headers["X-H1DS-dim-1-first"]);
		for (var i1=0; i1<dim_1_length; i1++){
		    if (ndim > 2) {
			output['data'][i0][i1] = [];
			var dim_2_length = parseInt(headers["X-H2DS-dim-2-length"]);
			var dim_2_delta = parseFloat(headers["X-H1DS-dim-2-delta"]);
			var dim_2_first = parseFloat(headers["X-H1DS-dim-2-first"]);
			for (var i2=0; i2<dim_2_length; i2++){
			    // TODO: only up to 3d supported, generalise
			    output['data'][i0][i1][i2] = data_delta*bin_data[counter]+data_min;
			    counter++;
			}
		    } else {
			//output['data'][i0][i1] = data_delta*bin_data[counter]+data_min;
			// TODO: putting back delta and min screw up the spectrogram, why?
			output['data'][i0][i1] = bin_data[counter];
			counter++;
		    }
		}		
	    } else {
		output['data'][i0] = data_delta*bin_data[counter]+data_min;
		counter++;
	    }
	}
    }
    return output;
}


// from http://updates.html5rocks.com/2012/06/How-to-convert-ArrayBuffer-to-and-from-String
// changed to Uint8Array for UTF-8
function ab2str(buf) {
    //return String.fromCharCode.apply(null, new Uint16Array(buf));
    return String.fromCharCode.apply(null, new Uint8Array(buf));
}
function str2ab(str) {
    //var buf = new ArrayBuffer(str.length*2); // 2 bytes for each char
    var buf = new ArrayBuffer(str.length);
    //var bufView = new Uint16Array(buf);
    var bufView = new Uint8Array(buf);
    for (var i=0, strLen=str.length; i<strLen; i++) {
        bufView[i] = str.charCodeAt(i);
    }
    return buf;
}
   

PlotContainer.prototype.loadURL = function(data_url, is_binary) {
    var that = this;
    // the actual data we request uses a modified URL which resamples the data to the screen resolution
    // does data_url contain a query string?
    //var query_char = data_url.match(/\?.+/) ? '&' : '?';
    //plot_data_url = data_url + (query_char+'f999_name=resample_minmax&f999_arg0='+(this.svg.attr("width"))+'&format=json');
    // TODO: we should be able to easily inspect returned data to see
    // if it is minmax, rather than needing a dedicated js function
    // TODO: refactor code to be able to cope with async URL loading.
    if (is_binary) {
	var response = $.ajax({url: data_url, 
		//dataType: "string",
		async:false
	       });
	var headers = ProcessH1DSHeaders(response.getAllResponseHeaders());
	response.done(function(a) {
	    data = ProcessBinaryData(a, headers);
	    //a.is_minmax = isMinMaxPlot(a);	    
	    // TODO: 1D signal dim might not be an element, so dim.length will be large...
	    // TODO:   - need to make this consistent b/w signals of different dim 
	    //a.n_dim = a.dim.length === 2 ? 2 : 1
	    that.url_cache[data_url] = data;
	});
    } else {
    $.ajax({url: data_url, 
	    dataType: "json",
	    async:false})
	.done(function(a) {
	    a.is_minmax = isMinMaxPlot(a);
	    // TODO: 1D signal dim might not be an element, so dim.length will be large...
	    // TODO:   - need to make this consistent b/w signals of different dim 
	    a.n_dim = a.dim.length === 2 ? 2 : 1
	    that.url_cache[data_url] = a;
	});
    }
};

PlotContainer.prototype.getData = function(data_id, plot_type) {
    var return_data = {};
    switch(plot_type) {
    case 'raw':
	var new_uri = getRawUri(this.data_ids[data_id].uri,this.svg.attr("width"));
	var rendered_uri = new_uri.renderUri()
	this.loadURL(rendered_uri, new_uri.isBinary());
	return_data = this.url_cache[rendered_uri];
	break;
    case 'spectrogram':
	var new_uri = getSpectrogramUri(this.data_ids[data_id].uri);
	var rendered_uri = new_uri.renderUri()
	this.loadURL(rendered_uri,  new_uri.isBinary());
	return_data = this.url_cache[rendered_uri];
	break;
    case 'powerspectrum':
	var new_uri = getPowerspectrumUri(this.data_ids[data_id].uri, this.svg.attr("width"));
	var rendered_uri = new_uri.renderUri()
	this.loadURL(rendered_uri,  new_uri.isBinary());
	return_data = this.url_cache[rendered_uri];
	break;
    default:
	this.loadURL(this.data_ids[data_id].uri,  false);
	return_data = this.url_cache[this.data_ids[data_id].uri];
	break;
    }
    return return_data;
}

PlotContainer.prototype.updateDisplay = function() {
    var that = this;

    // load data for plots...
    for (var plot_i=0;plot_i<this.plotGrid.length;plot_i++) {
	for (var data_i=0; data_i<this.plotGrid[plot_i].data_ids.length; data_i++) {
	    this.plotGrid[plot_i].data[data_i] = this.getData(this.plotGrid[plot_i].data_ids[data_i], this.plotGrid[plot_i].plotType);
	    this.plotGrid[plot_i].data[data_i].colour = that.data_ids[this.plotGrid[plot_i].data_ids[data_i]].colour;
	}
	if (this.plotGrid[plot_i].data_ids.length > 0) this.updatePlot(plot_i);
    }

    // link axes.
    for (var plot_i=0;plot_i<this.plotGrid.length;plot_i++) {
	if (this.plotGrid[plot_i].data_ids.length > 0) this.linkAxes(plot_i);
    }

    // ...
    var plots = this.svg.selectAll("g.plot")
	.data(this.plotGrid);

    plots.enter().append("g")
	.attr("class", "plot")
	.attr("transform", function(d) {return "translate("+d.translate[0]+","+d.translate[1]+")"})
	.append("clipPath")
	  .attr("id", function(d,i) {return "plot-"+i+"-clippath"})
	  .append("svg:rect")
	    .attr("width", function(d,i) {return d.width})
            .attr("height", function(d,i) {return d.height});

    plots.exit().remove();
    

    // ### Add axes ###
    // # x axis
    plots.append("g")
	.attr("class", "axis x")
	.attr("id", function(d,i) {return "plot-"+i+"-axis-x";})
	.attr("transform", function(d) {return "translate(0,"+(d.height-that.xAxisPadding)+")"})
	.each(function(d) { typeof d.xAxis !== 'undefined' ? d3.select(this).call(d.xAxis) : function(){}; })
	    .append("text")
	.attr("text-anchor", "middle")
	.attr("x", function(d) { return that.yAxisPadding+0.5*(d.width-that.yAxisPadding); })
	.attr("y", function(d) { return 0.8*that.xAxisPadding; })
	.text(function(d) { return "["+d.data[0].units[1]+"]"; }); // TODO: uses data[0], rather than data for this plot.

    // # y axis
    plots.append("g")
	.attr("class", "axis y")
	.attr("id", function(d,i) {return "plot-"+i+"-axis-y";})
	.attr("transform", function(d) {return "translate("+that.yAxisPadding+","+0+")"})
	.each(function(d) { typeof d.yAxis !== 'undefined' ? d3.select(this).call(d.yAxis) : function(){}; })
	    .append("text")
	.attr("text-anchor", "middle")
	.attr("transform", "rotate(-90)")
	.attr("x", function(d) { return -0.5*(d.height-that.xAxisPadding); })
	.attr("y", function(d) { return -0.8*that.yAxisPadding; })
	.text(function(d) { return "["+d.data[0].units[0]+"]"; }); // TODO: uses data[0], rather than data for this plot.


    var plotitems = plots
	.selectAll("g.data")
	.data(function(d,j) { 
	    var plot_data = [];
	    for (var i=0; i<d.data.length; i++) plot_data[i] = {'data':d.data[i], 'plot':d, 'plotid':j};
	    return plot_data;});
    
    plotitems.enter().append("g")
	.attr("class", "data")
	.attr("clip-path", function(d,i) { return "url(#plot-"+i+"-clippath)"})
	.each(function(d,i) {d3.select(this).call(that.plotTypes[d.plot.plotType]);});

    plotitems.exit().remove();
};

PlotContainer.prototype.linkAxes = function(plot_id) {
    var that = this;
    var use_x_id  = (this.plotGrid[plot_id].bindAxis[0] >= 0 && this.plotGrid[plot_id].bindAxis[0] !== plot_id)?this.plotGrid[plot_id].bindAxis[0]:plot_id;
    var use_y_id  = (this.plotGrid[plot_id].bindAxis[1] >= 0 && this.plotGrid[plot_id].bindAxis[1] !== plot_id)?this.plotGrid[plot_id].bindAxis[1]:plot_id;
    if (use_x_id !== plot_id) this.plotGrid[plot_id].x.domain(this.plotGrid[use_x_id].x.domain());
    if (use_y_id !== plot_id) this.plotGrid[plot_id].y.domain(this.plotGrid[use_y_id].y.domain());
    
};

PlotContainer.prototype.updatePlot = function(plot_id) {
    var that = this;
    var do_flip = this.plotGrid[plot_id].flip;

    //var use_x_id  = (this.plotGrid[plot_id].bindAxis[0] >= 0 && this.plotGrid[plot_id].bindAxis[0] !== plot_id)?this.plotGrid[plot_id].bindAxis[0]:plot_id;
    //var use_y_id  = (this.plotGrid[plot_id].bindAxis[1] >= 0 && this.plotGrid[plot_id].bindAxis[1] !== plot_id)?this.plotGrid[plot_id].bindAxis[1]:plot_id;

    // update the plot data list from the data_id list

    var horizontal_range = [that.yAxisPadding,this.plotGrid[plot_id].width];
    var vertical_range = [this.plotGrid[plot_id].height-that.xAxisPadding, 0];

    var dim_domain = [
	d3.min(this.plotGrid[plot_id].data, function(d,i) { return d.n_dim===1 ? d3.min(d.dim) : d3.min(d.dim[0]);}),
	d3.max(this.plotGrid[plot_id].data, function(d,i) { return d.n_dim===1 ? d3.max(d.dim) : d3.max(d.dim[0]);})
    ];

    var _x = d3.scale.linear()
	.range(do_flip?vertical_range:horizontal_range)
	.domain(dim_domain);
    
    if (this.plotGrid[plot_id].flip) {
	this.plotGrid[plot_id].y = _x;
    } else {
	this.plotGrid[plot_id].x = _x;
    }

    var data_domain = [
	d3.min(this.plotGrid[plot_id].data, function(d,i) {return d.n_dim === 1 ? (d.is_minmax ? d3.min(d.data[0]) : d3.min(d.data)) : d3.min(d.dim[1])}),
	d3.max(this.plotGrid[plot_id].data, function(d,i) {return d.n_dim === 1 ? (d.is_minmax ? d3.max(d.data[1]) : d3.max(d.data)) : d3.max(d.dim[1])})
    ];
    
    var data_span = data_domain[1]-data_domain[0];
    
    //this.plotGrid[plot_id].y = d3.scale.linear()
    var _y = d3.scale.linear()
	.range(do_flip?horizontal_range:vertical_range)
	.domain([
	    data_domain[0]-this.dataPadding*data_span,
	    data_domain[1]+this.dataPadding*data_span
	]);

    if (this.plotGrid[plot_id].flip) {
	this.plotGrid[plot_id].x = _y;
    } else {
	this.plotGrid[plot_id].y = _y;
    }


    //if (use_x_id !== plot_id) this.plotGrid[plot_id].x.domain(this.plotGrid[use_x_id].x.domain());
    //if (use_y_id !== plot_id) this.plotGrid[plot_id].y.domain(this.plotGrid[use_y_id].y.domain());

    this.plotGrid[plot_id].xAxis = d3.svg.axis()
	.scale(this.plotGrid[plot_id].x)
	.orient("bottom")
	.tickSize(this.plotGrid[plot_id].data[0].n_dim === 1 ? this.plotGrid[plot_id].y.range()[1]-this.plotGrid[plot_id].y.range()[0] : 5);

    this.plotGrid[plot_id].yAxis = d3.svg.axis()
	.scale(this.plotGrid[plot_id].y)
	.orient("left")
	.tickSize(this.plotGrid[plot_id].data[0].n_dim === 1 ? this.plotGrid[plot_id].x.range()[0]-this.plotGrid[plot_id].x.range()[1] : 5);

};


function getLastShotInDisplayedPage() {
    // get latest shot in document
    // TODO - this assumes shot is first column
    // if we get more flexible about the table/data structure
    // then we should get more clever about how we get this value
    var latest_shot = -1;
    d3.selectAll("table.main-table tr")
	.each(function(d,i) {
	    if (i > 0) {
		var shot = Number(d3.select(this).select("td").text());
		if (shot > latest_shot) {
		    latest_shot = shot;
		}
	    }
	}
	     );
    return latest_shot;
}


function summaryUpdateRequired(last_update) {
    //var latest_shot_in_doc = getLastShotInDisplayedPage();
    //var latest_summary_shot = -1;
    $.ajax({url: '/summary/_/get_last_update_time/', 
	    dataType: "json",
	    async:false})
	.done(function(a) {
	    //latest_summary_shot = Number(a.latest_shot);
	    latest_summdb_update = new Date(a.last_update);
	});
    return latest_summdb_update > last_update;
}

function updateSummaryDB() {
    var latest_shot_in_doc = getLastShotInDisplayedPage();
    var latest_summary_shot = -1;
    $.ajax({url: '/summary/_/get_latest_summarydb_shot/', 
	    dataType: "json",
	    async:false})
	.done(function(a) {
	    latest_summary_shot = Number(a.latest_shot);
	});

    if (latest_summary_shot > latest_shot_in_doc) {
	var query_char = window.location.search.length ? '&' : '?';
	var query_str = window.location.search + query_char + 'format=json';
	var json_url = window.location.toString()+query_str
	// keep async = false, to make sure we don't check document for 
	// current shot until we've updated the document.
	$.ajax({url: json_url, 
		dataType: "json",
		async:false})
	    .done(function(a) {
		// 
	    });
    }

}

function cross(a) {
    var data = [], di, ai, shot_dat;
    for (di=0;di<a.data.length;di++) {
	data[di] = [];
	data[di].shot
	for (ai=0; ai<a.attributes.length; ai++) {
	    data[di][ai] = {'shot':a.data[di].shot, 'attr':a.attributes[ai], 'value':a.data[di].d[ai]};
	}
    }
    return data;
}

$("span.toggleVertical").each(function() {
    if ($.cookie("vertical-"+$(this).text()) === "true") {
	$(this).toggleClass("verticalText");
	$(this).html($(this).text().replace(/(.)/g, "$1<br />"));
    }}
);


$("span.toggleVertical").click(function() {
    $(this).toggleClass("verticalText");
    if ($(this).hasClass("verticalText")) {
	$(this).html($(this).text().replace(/(.)/g, "$1<br />"));
	$.cookie("vertical-"+$(this).text(),true); 
	
    } else {
	$(this).html($(this).text().replace("$1<br />",""));
	$.cookie("vertical-"+$(this).text(),false); 
    }
});

function autoPollSummaryDB() {
    var do_poll = d3.select("#poll-summarydb-server");
    if (do_poll[0][0] !== null && do_poll.text() === 'True') {
	var last_update = null;
	var query_char = window.location.search.length ? '&' : '?';
	var query_str = window.location.search + query_char + 'format=json';
	var json_url = window.location.toString()+query_str	
	// select table elements
	var table = d3.select("table.main-table tbody");
	//var rows = table.selectAll("tr")
	//    .data([], function(d) {return d.shot;})
	//    .enter().append("tr")
	//    .each(function(d,i) {
	//	d3.select(this).selectAll("td").data(d.d).enter().append("td");
	//	// console.log(d);
	//    });

	function doSummaryUpdate(fade_duration) {
	    $.ajax({url: json_url, 
		    dataType: "json",
		    async:false})
		.done(function(a) {
		    /*
		    var rows = table.selectAll("tr")
			.data(a.data, function(d) { return d.shot;});
		    rows.enter()
			.insert("tr", "tr")
			.style('background-color', 'yellow')
			.each(function(d,i) {
			    d3.select(this).selectAll("td").data(d.d).enter()
				.append("td")
				.html(function(j,i){ return '<a href="/summary/_/go_to_source/'+a.attributes[i]+'/'+d.shot+'/" >'+j+'</a>'; });
			});
		    rows.transition()
			.duration(fade_duration)
			.style('background-color', 'white');
		    
		    rows.exit().remove();
		    */
		    last_update = new Date(a.timestamp);
		    var rows = table.selectAll("tr")
			.data(cross(a), function(d) { return d[0].shot;});
		    rows.enter()
			.insert("tr", "tr")
			.style('background-color', 'yellow');

		    var td = rows.selectAll("td")
			.data(function(d) { return d; });
		    td.enter()
			.append("td")
		    //.style('background-color', 'yellow')
			.html(function(d,i){ return '<a href="/summary/_/go_to_source/'+d.attr+'/'+d.shot+'/" >'+d.value+'</a>'; });
			//.text(function(d) { return d.value; });
		    
		    td.transition()
			.duration(500)
			//.styleTween('background-color', function tween(d, i, a) {console.log([d,i,a, this]); return d3.interpolate('yellow', 'white');})
			//.each(function(d) {console.log(d3.select(this))});
			.each(function(d) {
			    d3.select(this).html(function(d,i){ return '<a href="/summary/_/go_to_source/'+d.attr+'/'+d.shot+'/" >'+d.value+'</a>'; });
			    });
			//.text(function(d) {return d.value;});
			//.html(function(d,i){ return '<a href="/summary/_/go_to_source/'+d.attr+'/'+d.shot+'/" >'+d.value+'</a>'; });
			//.style('background-color', 'white');
			
		    rows.transition()
			.duration(fade_duration)
			.style('background-color', 'white');

		    rows.exit().remove();
			//.insert("tr", "tr")
			//.style('background-color', 'yellow')
			//.each(function(d,i) {
			//    d3.select(this).selectAll("td").data(d.d).enter()
		//		.append("td")
			// .html(function(j,i){ return '<a href="/summary/_/go_to_source/'+a.attributes[i]+'/'+d.shot+'/" >'+j+'</a>'; });
		//	});
		  //  rows.transition()
	//		.duration(fade_duration)
	//		.style('background-color', 'white');
		    
	//	    rows.exit().remove();
		});
	}
	doSummaryUpdate(1000);
	setInterval(function() {
	    if (summaryUpdateRequired(last_update)) {
		doSummaryUpdate(300000);
	    }
	}, 2000);
	//setInterval(function() {
	//    doSummaryUpdate(300000, last_update);
	//}, 2000);
    }
}

var shot_stream_client = new XMLHttpRequest();

function turnOffShotTracker() {
    $("#h1ds-track-latest-shot").hide();
    $("#h1ds-shot-controller").show();
    $("#h1ds-toggle-track-latest-shot").html('<FORM class="inline-form right" action="javascript:toggleTrackLatestShot()" method="post"><INPUT type="submit" id="h1ds-toggletrack-shot" name="h1ds-toggletrack-shot" value="track latest shot"></FORM>');
    $.cookie("shotTracking", 'false', {path:'/'});
    shot_stream_client.abort();
}

function turnOnShotTracker() {
    $("#h1ds-shot-controller").hide();
    $("#h1ds-track-latest-shot").show();
    $("#h1ds-toggletrack-latest-shot").html('<FORM class="inline-form right" action="javascript:toggleTrackLatestShot()" method="post"><INPUT type="submit" id="h1ds-toggletrack-shot" name="h1ds-toggletrack-shot" value="stop tracking latest shot"></FORM>');
    $.cookie("shotTracking", 'true', {path:'/'});

    shot_stream_client.open('get', '/_/shot_stream/');
    shot_stream_client.send();
    shot_stream_client.onprogress = function(){
	var split_response = this.responseText.split("\n");
	// -2 because each shot has a trailing \n
	var new_shot = split_response[split_response.length-2];
	$.getJSON("/_/url_for_shot",
		  {'input_path':window.location.toString(), 'shot':new_shot},
		  function(d){window.location = d.new_url;});
    };
}

function toggleTrackLatestShot() {
    // Keep toggle state in cookie so we can retain user preference through navigation etc.
    var currentState = $.cookie("shotTracking");
    if (currentState === 'true') {
	turnOffShotTracker();
    } else {
	turnOnShotTracker();
    }
    return false;
}  

function plotScalar(d, url) {
    return 0;
}

function plot1DimArray(d, url) {
    //var pc = new PlotContainer("#"+d, [300,250],[0.75,0.25]);
    var pc = new PlotContainer("#"+d, [500],[1.0]);
    pc.addData("default", url);
    
    //pc.setPlot(2, {"plotType":"spectrogram"});
    //pc.addDataToPlot("default", 2, false);
    
    //pc.setPlot(0, {"plotType":"raw", "bindAxis":[2,-1]});
    pc.setPlot(0, {"plotType":"raw"});
    //pc.addDataToPlot("default", 0, false);
    pc.addDataToPlot("default", 0, true);
    
    //pc.setPlot(3, {"plotType":"powerspectrum", "flip":true, 'bindAxis':[-1,2]});
    //pc.addDataToPlot("default", 3, true);

}

function plot2DimArray(d, url) {
	var pc = new PlotContainer("#"+d, [500],[1.0]);
	pc.addData("default", url);
	pc.setPlot(0, {"plotType":"raw2d"});
	pc.addDataToPlot("default", 0, true);
	
	//pc.setPlot(2, {"plotType":"spectrogram"});
	//pc.addDataToPlot("default", 2, false);

	//pc.setPlot(0, {"plotType":"raw", "bindAxis":[2,-1]});
	//pc.addDataToPlot("default", 0, false);

	//pc.setPlot(3, {"plotType":"powerspectrum", "flip":true, 'bindAxis':[-1,2]});
	//pc.addDataToPlot("default", 3, true);
}

function getPlotFunction(dtype, ndim) {
    // TODO: check dtype etc
    switch(ndim) {
	case "0":
	return plotScalar;
	break;
	case "1":
	return plot1DimArray;
	break;
	case "2":
	return plot2DimArray;
	break;
    }
}

function populatePagelet(d) {
    // get URL for pagelet data
    var pagelet_url = d.attr("data-pagelet-url");
    if (typeof pagelet_url === 'undefined') {
	pagelet_url = window.location.toString();
    }
    var _json_url = new H1DSUri(pagelet_url);
    _json_url.non_h1ds_query['format'] = 'json';
    var json_url = _json_url.renderUri();

    var dtype = d.attr("data-dtype");
    var ndim = d.attr("data-ndim");

    

    var plot_fn = getPlotFunction(dtype, ndim);
    plot_fn(d.attr("id"), json_url);
    /*
    $.ajax({url: data_url, 
	    dataType: "json",
	    async:true})
	.done(function(a) {
	    
	});
    */
    // console.log(d.attr("id"));
    //d.text(json_url);
}

//function populateTreeNav(navtree) {
//
//}

$.fn.scrollView = function () {
    return this.each(function () {
        $('html, body').animate({
            scrollTop: $(this).offset().top
        }, 0);
    });
}


$(document).ready(function() {
    $('#main').scrollView();
    autoPollSummaryDB();
    // autoUpdateEvents();
    loadCookie();
    $(".h1ds-pagelet").each(function() {
	populatePagelet($(this));
    });
    //$(".h1ds-tree-nav").each(function() {
//	populateTreeNav($(this));
 //   });
    //d3.json("http://bl.ocks.org/mbostock/raw/1093025/flare.json", function(json) {
    //json.x0 = 0;
    //json.y0 = 0;
    //updateNav(root = json);
    //});
    //tmp_json.x0 = 0;
    //tmp_json.y0 = 0;
    //var x = $("#test-nav").width();
    //$("#test-nav svg:svg").attr("width", x);
    
    //updateNav(root = tmp_json);
});


