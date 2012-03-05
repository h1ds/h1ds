// Custom javascript code for H1 data system
// David Pretty, 2010

var isOdd = function(someNumber){
    return (someNumber%2 == 0) ? false : true;
};


// Populate next level of mds tree navigation.

function populateMDSNav(tree, shot, current_node) {
	    if (current_node.hasClass("unpopulated")) {
		var nid=current_node.children(".mds-node-id").text();
		var node_tree=current_node.children(".mds-node-tree").text();
		var fetch_url='/mdsplus/mds_nav_subtree/'+node_tree+'/'+shot+'/'+nid+'/';
		$.getJSON(fetch_url, function(d){
			current_node.append('<ul class="mds-tree hidden"></ul>');
			var sub_node = current_node.children(".mds-tree");
			$.each(d.nodes, function(){
				sub_node.append('<li class="mds-node-item unpopulated"><span class="mds-node-name"><a href="'+this.url+'">'+this.name+'</a></span><span class="mds-node-id">'+this.nid+'</span><span class="mds-node-tree">'+this.tree+"</span></li>")
			    });
			if (sub_node.children(".mds-node-item").length > 0){
			    current_node.children(".mds-node-name").append(' \u00bb');
			}
		    }); // end getJSON
		current_node.removeClass("unpopulated");
		
		if (current_node.children(".mds-tree").children(".mds-node-item").length > 0) {
		    current_node.children(".mds-node-name").append(">");
		    
		}
		current_node.children(".mds-node-name").hover(function() {
			$(this).parent().children(".mds-tree").each(function() {
				$(this).removeClass("hidden");
				$(this).children(".mds-node-item").each(function() {
					populateMDSNav(tree, shot, $(this));
				    });
			    }); // each
		    });
	    } // if

    

} // function

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

function updateLatestShot() {
 $.getJSON('/mdsplus/latest_shot/{{input_tree}}/', function(d){
 $(".latest_shot").text(d.latest_shot);
 }); // end getJSON
} // end function

function autoUpdateLatestShot() {
    setInterval(updateLatestShot, 2000);
}

function formatDataForPlots(data) {
    // If we have min and max signals, then we fill the area between them.
    if (($.inArray("min", data.labels) > -1) && ($.inArray("max", data.labels) > -1) && (data.labels.length == 2)) {
	var d = {"signalmin":{"data": Array(data.data[0].length)},
		 "signalmax":{"data": Array(data.data[1].length)}};

	for( i=0; i < d.signalmin.data.length; i++){
            d.signalmin.data[i]=[data.dim[i],data.data[0][i]];
            d.signalmax.data[i]=[data.dim[i],data.data[1][i]];
	}
	var dataset = [{id: 'sigmin', data:d.signalmin.data, lines:{show:true, lineWidth:0.3, fill:false, shadowSize:0}, color:"rgba(50,50,255,0.5)"},
		       {id: 'sigmax', data:d.signalmax.data, lines:{show:true, lineWidth:0.3, fill:0.5, shadowSize:0}, color:"rgba(50,50,255,0.5)", fillBetween: 'sigmin'}];
	return dataset;	
    }
    
    else {
	var d = Array(data.data.length);
	for( i=0; i < d.length; i++){
            d[i]=[data.dim[i],data.data[i]];
	}
	var dataset = [{data:d, color:"rgb(50,50,255)"}];
	return dataset;
    }
} // end formatDataForPlots


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
	$(this).sortable('options');
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

}


function plotSignal2D() {
    // custom image manipulation for mds
    var container  = $("#signal-2d-placeholder");
    var query_char = window.location.search.length ? '&' : '?';
    var image_query = window.location.search + query_char + 'view=json';

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



//
// plotSignal1D
//
// For a given container div, we fetch data subsampled to the width of the plot window.
// The heights of the plots are fixed.
// Several plots are actally displayed. A large plot which allows zooming (TODO: and panning),
// and a smaller (smaller height) plot which shows the full signal and highlights the region shown in
// the larger plot. 
// An FFT of the signal in the large plot is also show.
// TODO: Allow both panning and zooming of plot
// TODO: more usable FFT plots, maybe a 2D spectrogram plot, which is selectable and applies filters 
// to the freq range selected. 
function plotSignal1D(id) {
    // get margins and plot width for container.
    var width_data = getPlotWidth(id);

    // compile the URL for retrieving subsampled data
    var query_char = window.location.search.length ? '&' : '?';
    var trace_query = window.location.search + query_char + 'view=json&f999_name=resample_minmax&f999_arg1='+width_data.plot;
    
    // spacing between bottom of plot and container.
    // TODO: should merge this with getPlotWidth to have a single
    // function which provides margins.
    var bottom_spacing = 20;

    // height of the signal plot 
    var signal_height = 200, overview_height = 100;


    // this is a bit convoluted, get the data, pass if to getFourier, which passes it to dataReady.
    // getFourier doesn't actually use the data which it takes as an argument! just passes it along.
    // TODO: refactor so it is more easily understandable.
    $.getJSON(trace_query, getFourier);

    function getFourier(d) {
	// compile the URL to get power spectrum data.
	var fourier_query = window.location.search + query_char + 'view=json&f990_name=power_spectrum&f995_arg0=0.0&f995_arg1=0.5&f995_name=norm_dim_range&f999_name=resample_minmax&f999_arg1='+width_data.plot;
	// get power spectrum data and pass the resampled data (which getFourier took as an argument) to dataReady.
	$.getJSON(fourier_query, function(a) { dataReady(d,a) ;});
    }

    function dataReady(signal_data, fourier_data) {
	var orig_data = signal_data;
	// how far past the min and max data values should the axes plot?
	// e.g. max y axis value = max_data + range_padding*(min_data - max_data)
	var range_padding = 0.05;
	// spacing between plots
	var plot_spacing = 25;

	// initially, the overview is the same as the signal data
	var data = [{'name':'signal','data':signal_data, 'height':signal_height},
		    {'name':'overview','data':orig_data, 'height':overview_height},
		    {'name':'fourier','data':fourier_data, 'height':overview_height}]


	// x and y are objects which will contain axes for each of the data plots/
	var x = {}, y={};
	// plot width
	var w = width_data.plot;// + 2*width_data.margin;
	//var m = width_data.margin;

	// populate x and y with axes.
	function setupAxes(d, i) {
	    y[d.name] = d3.scale.linear();
	    x[d.name] = d3.scale.linear();
	}

	// include additional info in data.
	function updateData(d, i) {
	    // offsets to determine vertical coordinates of each plot.
	    if (i > 0) {
		d.offset = d.height+data[i-1].offset+plot_spacing;
	    } else {
		d.offset = d.height;
	    }
	    // get min and max data values
	    d.is_minmax = isMinMaxPlot(d.data);
	    d.min_data = d.is_minmax ? d3.min(d.data.data[0]) : d3.min(d.data.data);
	    d.max_data = d.is_minmax ? d3.max(d.data.data[1]) : d3.max(d.data.data);

	    // get min and max values for axes
	    d.delta_data = d.max_data - d.min_data;
	    d.min_plot = d.min_data - range_padding*d.delta_data;
	    d.max_plot = d.max_data + range_padding*d.delta_data;

	    // get min and max dimension (i.e. x axis, e.g. time)
	    d.min_dim = d.data.dim[0];
	    d.max_dim = d.data.dim[d.data.dim.length-1];

	    // recompute axes
	    y[d.name].domain([d.min_data, d.max_data]).range([0 + range_padding*d.height, d.height*(1-range_padding)]);
	    x[d.name].domain([d.min_dim, d.max_dim]).range([0 + width_data.marginLeft, w - width_data.marginRight]);	    
	}

	// apply the above axes and data functions
	data.forEach(setupAxes);
	data.forEach(updateData);

	// fix height of container element
	$(id).height(data[data.length -1].offset+bottom_spacing);

	// add to the container the SVG element which will contain the plots.
	var svg = d3.select(id)
	    .append("svg:svg")
	    .attr("width", w)
	    .attr("height", data[data.length -1].offset+bottom_spacing);
	
	// add an SVG group ('g') container element for each plot.
	var g = svg.selectAll("g")
	    .data(data)
	    .enter().append("svg:g")
	    .attr("transform", function(d) {return "translate(0, "+d.offset+")" });

	// for each data group, add an SVD path element with the data.
	g.append("svg:path")
	    .attr("class", "plot")
	    .classed("path-filled", function(d) { return d.is_minmax })
	    .attr("d", doLine);


	// TODO: surely these can be replaced with d3 scales?
	function minX(d) { return x[d.name](d.min_dim); }
	function maxX(d) { return x[d.name](d.max_dim); }
	function minY(d) { return -1 * y[d.name](d.min_plot); }
	function maxY(d) { return -1 * y[d.name](d.max_plot); }
	
	// create a brush objects
	var br = d3.svg.brush()
	    .on("brushstart", brushstart)
	    .on("brush", brush)
	    .on("brushend", brushend);
	
	// this should be added by brush.js?
	// probably we just need something else with .background
	// and brush.js will insert?
	// TODO: do we need this?
	g.append("rect")
            .attr("class", "background")
            .style("visibility", "hidden")
            .style("pointer-events", "all")
            .style("cursor", "crosshair")
	    .attr("x", minX)
	    .attr("y", maxY)
	    .attr("width", function(d) {return maxX(d)-minX(d)})
	    .attr("height", function(d) {return minY(d)-maxY(d)}); 


	// for each plot, call the brush and set the brush to the plot's x axis
	g.each( function (d) { d3.select(this).call(br.x(x[d.name]))});

	// fix the y range for the brush rectangles. 
	// TODO: do we need this?
	g.selectAll("rect.extent")
	    .attr("y", maxY)
	    .attr("height", function(d) {return minY(d)-maxY(d)});

	//
	// Brush functions
	//

	// called when brush starts
	function brushstart(p) {
	    g.classed("selecting", true);
	    br.x(x[p.name]);
	}


	// called when brush is dragged
	function brush() {
	    var s = d3.event.target.extent();
	}

	// called when brush is finished (user unclicks the mouse)
	function brushend() {
	    g.classed("selecting", !d3.event.target.empty());
	    var s = d3.event.target.extent();
	    var new_data_url = window.location.search + query_char + 'f990_name=dim_range&f990_arg0='+s[0]+'&f990_arg1='+s[1]+'&view=json&f999_name=resample_minmax&f999_arg1='+width_data.plot;

	    function updateFourier(d) {
		var fourier_query = window.location.search + query_char + 'f980_name=dim_range&f980_arg0='+s[0]+'&f980_arg1='+s[1]+'&view=json&f990_name=power_spectrum&f995_arg0=0.0&f995_arg1=0.5&f995_name=norm_dim_range&f999_name=resample_minmax&f999_arg1='+width_data.plot;
		
		$.getJSON(fourier_query, function(a) { updatePlot(d,a) ;});
	    }
	    d3.json(new_data_url, updateFourier);

	}

	
	function updatePlot(newdata, newfourier) {
	    
	    var ndat = [{'name':'signal','data':newdata, 'height':signal_height},
			{'name':'overview', 'data':orig_data, 'height':overview_height},
			{'name':'fourier','data':newfourier, 'height':overview_height}];

	    ndat.forEach(updateData);

	    g.data(ndat).select("path.plot")
		.classed("path-filled", function(d, i) { return d.is_minmax })
		.transition().duration(10).attr("d", doLine);
	    
	    g.selectAll(".xLabel").remove();
	    g.selectAll(".xTicks").remove();
	    g.selectAll(".yLabel").remove();
	    g.selectAll(".yTicks").remove();

	    updateAxesMarkers();


	    g.each(function(d,i) {
		    d3.select(this).call(br.clear());
		if (i == 1 ) {
		    d3.select(this).selectAll("rect.highlight").remove();
		    d3.select(this).append("rect")
			.attr("class", "highlight")
			.attr("x", x['overview'](ndat[0].min_dim))
			.attr("width", x['overview'](ndat[0].max_dim)-x['overview'](ndat[0].min_dim) )
			.attr("y", -1*y['overview'](ndat[1].max_plot))
			.attr("height", -1*(y['overview'](ndat[1].min_plot) - y['overview'](ndat[1].max_plot)));
		    
		}
	    });

	}




	function doLine(d, i) {
	    if (d.is_minmax) {
		var fill_data = fillPlot(d.data);
		var line = d3.svg.line()
		    .x(function(a) {return x[d.name](a[0]); })
		    .y(function(a) {return -1 * y[d.name](a[1]); });
		return line(fill_data);
	    } else {
		var line = d3.svg.line()
		    .x(function(a,j) { return x[d.name](d.data.dim[j]); })
		    .y(function(a) { return -1 * y[d.name](a); });
		return line(d.data.data);
	    }
	}
	function xTicksWithData(d) {
	    var t = [];
	    var n = 5;
	    var xticks = x[d.name].ticks(n);
	    var xticklabels = x[d.name].tickFormat(n);
	    for (var i=0; i < xticks.length; i++) t.push({'d':d, 't':xticks[i], 'lab':xticklabels});
	    return t;
	}
	function yTicksWithData(d) {
	    var t = [];
	    var n = 5;
	    var yticks = y[d.name].ticks(n);
	    var yticklabels = y[d.name].tickFormat(n);
	    for (var i=0; i < yticks.length; i++) t.push({'d':d, 't':yticks[i], 'lab':yticklabels});
	    return t;
	}


	// x axis
	g.append("svg:line")
	    .attr("x1", minX)
	    .attr("y1", minY)
	    .attr("x2", maxX)
	    .attr("y2", minY);
	g.append("svg:line")
	    .attr("x1", minX)
	    .attr("y1", maxY)
	    .attr("x2", maxX)
	    .attr("y2", maxY);

	// y axis
	g.append("svg:line")
	    .attr("x1", minX)
	    .attr("y1", minY)
	    .attr("x2", minX)
	    .attr("y2", maxY);
	g.append("svg:line")
	    .attr("x1", maxX)
	    .attr("y1", minY)
	    .attr("x2", maxX)
	    .attr("y2", maxY);

	function updateAxesMarkers() {

	g.selectAll(".xLabel")
	    .data(xTicksWithData)
	    .enter().append("svg:text")
	    .attr("class", "xLabel")
	    .text(function(a) { return a.lab(a.t) })
	    .attr("x", function(a) { return x[a.d.name](a.t) })
	    .attr("y", function(a) { return -1*(y[a.d.name](a.d.min_plot)-10) })
	    .attr("text-anchor", "middle");

	g.selectAll(".yLabel")
	    .data(yTicksWithData)
	    .enter().append("svg:text")
	    .attr("class", "yLabel")
	    .text(function(a) { return a.lab(a.t) })
	    .attr("x", function(a) { return x[a.d.name](a.d.min_dim)-30 })
	    .attr("y", function(a) { return -1*y[a.d.name](a.t) } )
	    .attr("text-anchor", "right")
	    .attr("dy", 4);

	g.selectAll(".xTicks")
	    .data(xTicksWithData)
	    .enter().append("svg:line")
	    .attr("class", "xTicks")
	    .attr("x1", function(a) { return x[a.d.name](a.t); })
	    .attr("y1", function(a) { return -1 * y[a.d.name](a.d.min_plot) })
	    .attr("x2", function(a) { return x[a.d.name](a.t); })
	    .attr("y2", function(a) { return -1 * (y[a.d.name](a.d.max_plot))});

	g.selectAll(".yTicks")
	    .data(yTicksWithData)
	    .enter().append("svg:line")
	    .attr("class", "yTicks")
	    .attr("y1", function(a) { return -1 * y[a.d.name](a.t); })
	    .attr("x1", function(a) { return x[a.d.name](a.d.min_dim) })
	    .attr("y2", function(a) { return -1 * y[a.d.name](a.t); })
	    .attr("x2", function(a) { return x[a.d.name](a.d.max_dim) });

	}

	updateAxesMarkers();

    }    
}

$(document).ready(function() {
    // updateLatestShot();
    // autoUpdateLatestShot();
    // autoUpdateEvents();
    loadCookie();
    var shot=$('#mds-nav-shot').text();
    var tree=$('#mds-nav-treename').text();
    $(".mds-node-item").each(function() {
	populateMDSNav(tree, shot, $(this));
    });
    if ($("#signal-1d-placeholder").length) {
	data = plotSignal1D("#signal-1d-placeholder");
    }
    if ($("#signal-2d-placeholder").length) {
	plotSignal2D();
    }
    if ($("#signal-3d-placeholder").length) {
	data = plotSignal3D();
    }

});


