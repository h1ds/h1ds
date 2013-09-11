////////////////////////////////////////////////////////////////////////
// Custom javascript code for H1 data system
// David Pretty, 2010-2013
////////////////////////////////////////////////////////////////////////

var golden_ratio = 1.61803398875;


////////////////////////////////////////////////////////////////////////
// Masonry - for  grid layout. Currently just used in  homepage, but not
// really needed there.
////////////////////////////////////////////////////////////////////////

$('#masonry-container').masonry({
     itemSelector: '.mbox',
     columnWidth: 384
 });

////////////////////////////////////////////////////////////////////////
// scrollView - scroll to specified element
////////////////////////////////////////////////////////////////////////

$.fn.scrollView = function () {
    return this.each(function () {
        $('html, body').animate({
            scrollTop: $(this).offset().top
        }, 0);
    });
}

////////////////////////////////////////////////////////////////////////
// jQuery UI Portlets
// Adapted from http://jqueryui.com/demos/sortable/#portlets
////////////////////////////////////////////////////////////////////////

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


////////////////////////////////////////////////////////////////////////
// Cookie management
////////////////////////////////////////////////////////////////////////

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

////////////////////////////////////////////////////////////////////////
// Latest shot tracking
////////////////////////////////////////////////////////////////////////


var shot_stream_client = new XMLHttpRequest();

// TODO: rather not have big chunks of html here - use js instead, eg http://stackoverflow.com/questions/3365325/form-action-javascriptblock-redirects-to-javascriptblock-url-in-firefo
function turnOffShotTracker() {
    $("#h1ds-track-latest-shot").hide();
    $("#h1ds-shot-controller").show();
    $("#h1ds-toggle-track-latest-shot").html('<FORM class="inline-form right" action="." onsubmit="javascript:toggleTrackLatestShot()" method="post"><INPUT type="submit" id="h1ds-toggletrack-shot" name="h1ds-toggletrack-shot" value="track latest shot"></FORM>');
    $.cookie("shotTracking", 'false', {path:'/'});
    shot_stream_client.abort();
}

// TODO: rather not have big chunks of html here - use js instead, eg http://stackoverflow.com/questions/3365325/form-action-javascriptblock-redirects-to-javascriptblock-url-in-firefo
function turnOnShotTracker() {
    $("#h1ds-shot-controller").hide();
    $("#h1ds-track-latest-shot").show();
    $("#h1ds-toggletrack-latest-shot").html('<FORM class="inline-form right" action="." onsubmit="javascript:toggleTrackLatestShot()" method="post"><INPUT type="submit" id="h1ds-toggletrack-shot" name="h1ds-toggletrack-shot" value="stop tracking latest shot"></FORM>');
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


////////////////////////////////////////////////////////////////////////
// Short polling for Summary database
// TODO: use SSE instead!!
////////////////////////////////////////////////////////////////////////

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


////////////////////////////////////////////////////////////////////////
// Mouse controls for data zooming etc.
////////////////////////////////////////////////////////////////////////

d3.select(window)
    .on("mousemove", mousemove)
    .on("mouseup", mouseup);

var rect, x0, x1, count, par_rect;

function mousedown() {
    x0 = d3.mouse(this);
    count = 0;
    par_rect = d3.select(this);
    rect = d3.select(this.parentNode)
	.append("svg:rect")
	.attr("y", par_rect.attr("y"))
	.attr("height", par_rect.attr("height"))
        .style("fill", "#999")
        .style("fill-opacity", .5);
    
    d3.event.preventDefault();
}

function mousemove() {
    if (!rect) return;
    //x1 = d3.svg.mouse(rect.node());
    x1 = d3.mouse(rect.node());
    // TODO: put elsewhere
    var size = 150, padding = 20;

    //x1[0] = Math.max(padding / 2, Math.min(size - padding / 2, x1[0]));
    //x1[1] = Math.max(padding / 2, Math.min(size - padding / 2, x1[1]));

    var minx = Math.min(x0[0], x1[0]),
        maxx = Math.max(x0[0], x1[0]),
        miny = Math.min(x0[1], x1[1]),
        maxy = Math.max(x0[1], x1[1]);

    rect
        .attr("x", minx - .5)
        //.attr("y", miny - .5)
        .attr("width", maxx - minx + 1)
        //.attr("height", maxy - miny + 1);


}

function mouseup() {
    if (!rect) return;
    var tmp = rect;
    rect.each(function(d){
	// this probably shouldn't be within a .each()
	var new_minx = d.xAxis.scale().invert(d3.select(this).attr("x"));
	var new_maxx = d.xAxis.scale().invert(+d3.select(this).attr("x") + +d3.select(this).attr("width"));
	var thisURI = new H1DSUri(window.location.href);
	var next_index = Number(thisURI.getNextFilterID());
	if (next_index == 0) {	    
	    thisURI.appendFilter("dim_range", {'min':new_minx, 'max':new_maxx});
	} else {
	    var last_index = next_index - 1;
	    if (thisURI.h1ds_filters[String(last_index)].name === "dim_range") {
		thisURI.h1ds_filters[String(last_index)].kwargs = {"min":new_minx, "max":new_maxx};
	    } else {
		thisURI.appendFilter("dim_range", {'min':new_minx, 'max':new_maxx});
	    }
	}
	$(".h1ds-pagelet").each(function() {
	    d3.select(this).html(''); // clear out the old (hack - not very d3ish to delete and readd)
	    populatePagelet($(this), thisURI.renderUri()); // and bring in the new
	});
	if (Modernizr.history) {
	    history.pushState(null, null, thisURI.renderUri());
	} // TODO: if not, shoudl we refresh the page so that URI is consistent?

    })
    rect.remove();
    rect = null;
}


// Functions to modify a URL to return data suitable for a given plot type

function getSpectrogramUri(original_uri) {
    // assume original_url gives a timeseries.
    var h1ds_uri = new H1DSUri(original_uri);
    h1ds_uri.addExtraFilter('slanted_baseline', {'window':10});
    h1ds_uri.addExtraFilter('spectrogram', {'bin_size':-1});
    h1ds_uri.addExtraFilter('norm_dim_range_2d', {'x_min':0, 'x_max':1, 'y_min':0, 'y_max':0.5});
    h1ds_uri.addExtraFilter('y_axis_energy_limit', {'threshold':0.995});
    h1ds_uri.extra_non_h1ds_query['format'] = 'bin';
    h1ds_uri.extra_non_h1ds_query['bin_assert_dtype'] = 'uint8';
    return h1ds_uri;
}

function getPowerspectrumUri(original_uri, width) {
    // assume original_url gives a timeseries.
    var h1ds_uri = new H1DSUri(original_uri);
    h1ds_uri.addExtraFilter('slanted_baseline', {'window':10});
    h1ds_uri.addExtraFilter('power_spectrum', {});
    h1ds_uri.addExtraFilter('norm_dim_range', {'min':0,'max':0.5});
    //h1ds_uri.addExtraFilter('x_axis_energy_limit',{'threshold':0.995});
    h1ds_uri.addExtraFilter('resample_minmax', {'n_bins':width});
    h1ds_uri.extra_non_h1ds_query['format'] = 'json';
    return h1ds_uri;
}

function getRawUri(original_uri, width) {
    // assume original_url gives a timeseries.
    var h1ds_uri = new H1DSUri(original_uri);
    h1ds_uri.addExtraFilter('resample_minmax', {'n_bins':width});
    h1ds_uri.extra_non_h1ds_query['format'] = 'json';
    return h1ds_uri;
}

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



////////////////////////////////////////////////////////////////////////
// loadPlotState
// load the  data required for  plotting etc,  to be handled  by HTML5
// history API
////////////////////////////////////////////////////////////////////////

/*
 * Data format (TODO: document this somewhere more visible when the format is more settled).
 * 
 * Data format to be passed to plots = list of data object
 *
 * [data1, data2, data3, ....]
 *
 * data = {
 *    dimension: [dim1, dim2, ...],
 *    dimension_dtype: str,
 *    dimension_units: str,
 *    metadata: {key1:val1, key2:val2, ...},
 *    name: str,
 *    value: [ch1, ch2, ...],
 *    value_dype: str,
 *    value_units: str,
 * }
 *
 */
/*
function loadPlotState() {
    //TODO: should  we use urlcache  to share data between  charts, or
    //can   we   assume   each   chart  will   have   different   data
    //(e.g. different width rebinning etc)
    // worksheet_mode - don't assume the browser url points to a node.
    plotState.settings = {'edit_mode': false, 'worksheet_mode': false};
    plotState.url_cache = {};
    plotState.pagelets = [];
    $(".h1ds-pagelet").each(function(i, e) {
	loadPageletPlotState(i,e);
    });
}

function loadPageletPlotStateFromURL(i, e) {
    // TODO
    plotState.pagelets[i] = null;
}

function loadDefaultPageletPlotState(i, e) {
    // if the URL  query string does not specify  pagelet layout, then
    // by  default we  make a  10x10 grid  with a  single "raw"  chart
    // filling the whole pagelet.
    var pagelet_plotstate = {};
    var default_url = window.location.toString();
    var elmt = $(e);

    // pagelet margins
    pagelet_plotstate.margin = {top: 1, right: 1, bottom: 1, left: 1};

    // default grid is 10x10
    pagelet_plotstate.n_rows = 10;
    pagelet_plotstate.n_columns = 10;
    
    pagelet_plotstate.width = elmt.width() - pagelet_plotstate.margin.left - pagelet_plotstate.margin.right;
    // TODO: allow more flexibiity with height - e.g. user resize portlet
    pagelet_plotstate.height = Math.round(d3.min([pagelet_plotstate.width/golden_ratio, 0.9*$(window).height()]));
    pagelet_plotstate.dtype = elmt.attr("data-dtype");
    pagelet_plotstate.ndim = elmt.attr("data-ndim");

    
    // default  is a  single chart  fill the  whole grid,  showing raw
    // data.
    chart_state = {};
    chart_state.x0 = 0;
    chart_state.y0 = 0;
    chart_state.x1 = 10;
    chart_state.y1 = 10;
    // TODO - match default chart type to dtype & ndim
    chart_state.chart_type = "raw";
    chart_state.chart_width = ((chart_state.x1 - chart_state.x0)/pagelet_plotstate.n_columns)*pagelet_plotstate.width;
    chart_state.stateIndex = [0, 0]; // pagelet number, chart number - TODO: make this work for multiple pagelets & charts

    chart_state.data = [{}];
    chart_state.data[0].uri = getRawUri(default_url, chart_state.chart_width);
    chart_state.data[0].data = null;

    // insert the pagelet state into plotState
    pagelet_plotstate.charts = [chart_state];
    plotState.pagelets[i] = pagelet_plotstate;

    // load data asynchronously

    $.ajax({url: plotState.pagelets[i].charts[0].data[0].uri.renderExtraUri(),
	    dataType: "json",
	    async:true})
	.done(function(a) {
	    plotState.pagelets[i].charts[0].data[0].data = a;
	    // by updating asyncronousely,  this will probably interrupt
	    // existing updates when  each data comes in...  it may look
	    // messy...
	    // TODO: should we use queue.js when loading all data?
	    // https://github.com/mbostock/queue
	    // (and load visuals once all data is loaded?)
	    updateCharts();
	    //console.log("loaded data for pagelet "+i);
	});
    //console.log("finished state for pagelet "+i)
}

function loadPageletPlotState(i, e) {
    // arguments:
    // i: index of h1ds-pagelet (first is 0).
    // e: h1ds-pagelet element
    var elmt = $(e);
   
    loadPageletPlotStateFromURL(i,e);

    if (plotState.pagelets[i] === null) {
	loadDefaultPageletPlotState(i,e);
    }
}

//
//function updatePagelets() {
//    $(".h1ds-pagelet").each(function() {
//	
//    }
//}

// Base chart with features common to all h1ds charts...
// Note: follow conventions for margins: http://bl.ocks.org/mbostock/3019563
d3.chart("H1DSBaseChart", {
    initialize: function() {
	
	var chart = this;
	var background = this.base.append("g")
	    .classed("graph-background", true);
	
	chart.main = chart.base.append("g")
	    .attr("class", "chart-main");

	chart.brush = d3.svg.brush();

	// default
	chart.margin = {top: 10, right: 10, bottom: 10, left: 10};

	// set defaults 
	chart._width = 100;
	chart._height = 100;

	this.set_margin =  function(newMargin) {
	    var full_width = chart._width + chart.margin.left + chart.margin.right;
	    var full_height = chart._height + chart.margin.bottom + chart.margin.top;
	    
	    chart.margin = newMargin;
	    chart.base.select("g.chart-main")
		.attr("transform", "translate(" + chart.margin.left + "," + chart.margin.top + ")");

	    chart._width = full_width - chart.margin.left - chart.margin.right;
	    chart._height = full_height - chart.margin.top - chart.margin.bottom;
	};

	this.set_margin({top: 10, right: 10, bottom: 10, left: 10});

	this.layer("background", background, {
	    dataBind: function(data) {
		return this.selectAll("rect.background").data([data]);
	    },
	    insert: function() {
		return this.insert("rect")
		.attr("class", "background")
		.attr("x", 0)
		.attr("y", 0)
		.attr("width", chart._width+chart.margin.left+chart.margin.right)
		.attr("height", chart._height+chart.margin.top+chart.margin.bottom)
	    }
	    
	});
    },
    
    width: function(newWidth) {
	// for external calls, we care about the total width (incl margins)
	// internally we use the margin convention http://bl.ocks.org/mbostock/3019563
	// to avoid too much confusion, we use _width internally rather than have 
	// different values from width and width()
	if (!arguments.length) {
	    return this._width + this.margin.left + this.margin.right; 
	}

	this._width = newWidth - this.margin.left - this.margin.right;
	
	// the background uses the full width (including margins).
	this.base.select("g rect.background")
	    .attr("width", newWidth);
	
	return this;	
    },
    height: function(newHeight) {
	// see notes for width method
	if (!arguments.length) {
	    return this._height + this.margin.top + this.margin.bottom;
	}

	this._height = newHeight - this.margin.top - this.margin.bottom;
	
	// the background uses the full width (including margins).
	this.base.select("g rect.background")
	    .attr("y", newHeight)
	    .attr("height", newHeight);
	
	return this;	
    }
    
});


// a chart for testing... 
d3.chart("H1DSBaseChart").extend("H1DSTestChart", {
    initialize: function () {
	var chart = this;

	this.set_margin({top: 50, right: 50, bottom: 50, left: 50});

	this.xScale = d3.scale.linear()
	    .range([0, chart._width]);

	this.yScale = d3.scale.linear()
	    .range([chart._height, 0]);

	this.xAxis = d3.svg.axis()
	    .scale(this.xScale)
	    .orient("bottom");

	this.yAxis = d3.svg.axis()
	    .scale(this.yScale)
	    .orient("left");


	// this limits us to 10 signals. it gives us 2 colours per signal, one for outline, one for the fill (if required).
	this.colors = d3.scale.category20();

	this.layer("xAxis", chart.main.append("g"), {
	    dataBind: function(data) {
		// TODO: chart.data should be [data1, data2, etc...] so we can overplot
		chart.data = data[0];
		return this.selectAll("g.x.axis").data([data]);
	    },
	    insert: function() {
		return this.insert("g")
		    .attr("class", "x axis")
	    	    .attr("transform", function (d) {return "translate(" + 0 + "," + chart._height + ")";});
		
	    },
	    events: {
		"merge": function() {
		    chart.xScale
			.range([0, chart._width])
			.domain([d3.min(chart.data.dimension, function(v) {return d3.min(v); }),
				 d3.max(chart.data.dimension, function(v) {return d3.max(v); })]);
		    return this.call(chart.xAxis);
		},
		"enter": function() {
		    chart.xScale
			.range([0, chart._width])
			.domain([d3.min(chart.data.dimension, function(v) {return d3.min(v); }),
				 d3.max(chart.data.dimension, function(v) {return d3.max(v); })]);
		    
		    return this.call(chart.xAxis);		
		},
		"exit": function() {return this.remove()}
	    }
	});
	
	this.layer("yAxis", chart.main.append("g"), {
	    dataBind: function(data) {
		// TODO: shouldn't need to attach data for each layer?
		chart.data = data[0];

		return this.selectAll("g.y.axis").data([data]);
	    },
	    insert: function() {
		return this.append("g")
		    .attr("class", "y axis")
	    	    .attr("transform", function (d) {return "translate(" + 0 + "," + 0 + ")";});
	    },
	    events: {
		"merge": function() {
		    // we find min and max and add 5% to above and below.
		    var minval = d3.min(chart.data.value, function(v) {return d3.min(v); });
		    var maxval = d3.max(chart.data.value, function(v) {return d3.max(v); });
		    var delta = 0.05*(maxval - minval);
		    chart.yScale
			.range([chart._height, 0])
			.domain([minval-delta, maxval+delta]);
		    
		    return this.call(chart.yAxis);
		},
		"enter": function() {
		    // we find min and max and add 5% to above and below.
		    var minval = d3.min(chart.data.value, function(v) {return d3.min(v); });
		    var maxval = d3.max(chart.data.value, function(v) {return d3.max(v); });
		    var delta = 0.05*(maxval - minval);
		    chart.yScale
			.range([chart._height, 0])
			.domain([minval-delta, maxval+delta]);
		    return this.call(chart.yAxis);
		},
		"exit": function() {return this.remove()}
	    }
	});

	var line = d3.svg.line()
	    .x(function(d) { return chart.xScale(d[0]); })
	    .y(function(d) { return chart.yScale(d[1]); });
	
	// join n-th signal and dim together as [[s0,d0], [s1, d1], ...]
	// assume 1D (d.dimension has only one vector)
	// TODO - replace by format_data
	var join_data = function(d, n) {
	    var new_data = [];
	    for (var i=0; i<d.value[n].length; i++) {
		new_data.push([d.dimension[0][i], d.value[n][i]]);
	    }
	    return new_data;
	};

	// read in the data values provided and give back list of [x,y] for each data series
	// the lists have a boolean property 'closeLine', if true, the line will be closed
	// the lists have a boolean property 'fillLine', if true, the line will be filled..
	var format_data = function(data) {
	    var output_data = [];
	    // minmax pairs use up 2 channels but are combined here as a single line
	    var n_minmax_pairs = 0;
	    if (typeof data.metadata.minmax_pairs !== 'undefined') {
		n_minmax_pairs = data.metadata.minmax_pairs.length;
	    }
	    var non_minmax_indices = d3.range(data.value.length);
	    // first, get the minmax pairs
	    if (n_minmax_pairs > 0) {
		for (var i=0; i<n_minmax_pairs; i++) {
		    non_minmax_indices.splice(non_minmax_indices.indexOf(data.metadata.minmax_pairs[i][0]), 1);
		    non_minmax_indices.splice(non_minmax_indices.indexOf(data.metadata.minmax_pairs[i][1]), 1);
		    
		    var tmp_output_data = [];
		    for (var j=0; j<data.value[data.metadata.minmax_pairs[i][0]].length; j++) {
			tmp_output_data.push([data.dimension[0][j], data.value[data.metadata.minmax_pairs[i][0]][j]]);
		    }
		    
		    for (var j=data.value[data.metadata.minmax_pairs[i][1]].length-1; j>=0; j--) {
			tmp_output_data.push([data.dimension[0][j], data.value[data.metadata.minmax_pairs[i][1]][j]]);
		    }
		    tmp_output_data['closeLine'] = true;
		    tmp_output_data['fillLine'] = true;
		    output_data.push(tmp_output_data);
		    
		}
	    }
	    
	    for (var i=0; i<non_minmax_indices.length; i++) {
		var ch_i = non_minmax_indices[i];
		var tmp_output_data = [];
		for (var j=0; j<data.value[ch_i].length; j++) {
		    tmp_output_data.push([data.dimension[0][j], data.value[ch_i][j]]);
		}
		tmp_output_data['closeLine'] = false;
		tmp_output_data['fillLine'] = false;
		output_data.push(tmp_output_data);
	    }
	    
	    return output_data;

	};

	this.layer("data", chart.main.append("g"), {
	    dataBind: function(data) {
		chart.data = data[0];
		return this.selectAll("path.signal").data(format_data(chart.data));
	    },
	    insert: function() {
		return this.append("path");
	    },
	    events: {
		"merge": function() {
		    return this
			.attr("class", "signal")
			.style("stroke", function(d, i) { return chart.colors(2*i); })
			.style("fill", function(d, i) {return (d.fillLine ? chart.colors(2*i+1) : "none"); })
			.attr("d", function(d,i) {return line(d) + (d.closeLine ? "Z" : "");});
		},
		
		"enter": function() {
		    return this
			.attr("class", "signal")
			.style("stroke", function(d, i) { return chart.colors(2*i); })
			.style("fill", function(d, i) {return (d.fillLine ? chart.colors(2*i+1) : "none"); })
			.attr("d", function(d,i) {return line(d) + (d.closeLine ? "Z" : "");});
		},
		"exit": function() {return this.remove()}
	    }
	});

	var load_selection = function() {
	    // TODO: HACK - use stateindex rather than assume 0!!!

	    var current_uri = plotState
		.pagelets[0]
		.charts[0]
		.data[0].uri;

	    // create  a new  base  URI (i.e.  in location  base)  with the  new
	    // dim_range 
	    // NOTE: this  is for 1d  signals - this  method is still  a testing
	    // plot, but really assumes 1d data for the moment.
	    // TODO: abstract  out the  bits which  can be  used for  other plot
	    // types
	    // if the last  main_h1ds_filter is dim_range, then  we overwrite it
	    // (save the server  doing a needless dim_range).  Otherwise we just
	    // append the dim_range  filter (so we don't  interfere with filters
	    // coming after an existing dim_range filter, if there is one).
	    // 

	    var dr_kwargs = {'min':chart.brush.extent()[0], 'max':chart.brush.extent()[1]};
	    var new_uri = new H1DSUri(current_uri.base_uri);
	    new_uri.updateOrAddBaseFilter("dim_range", dr_kwargs);

	    // set up dim_range filter

	    // TODO: hard coded for raw URI...
	    // TODO: perhaps getRawUri should figure out the width it needs?
	    new_uri = getRawUri(new_uri.renderBaseUri(), (chart._width + chart.margin.left + chart.margin.right));
	    
	    plotState // SAME HACK
		.pagelets[0]
		.charts[0]
		.data[0].uri = new_uri;

	    $.ajax({url: new_uri.renderExtraUri(),
		    dataType: "json",
		    async:false})
		.done(function(a) {
		    plotState //same HACK
			.pagelets[0]
			.charts[0]
			.data[0].data = a;
		    chart.draw([a.data]); // TODO: make sure we're not missing any hacks in updateCharts.
		    // TODO: pushstate, use base_uri..
		});
	    
	};

	this.layer("interactive", chart.main, {
	    dataBind: function(data) {
		chart.data = data[0];
		return this.selectAll("g.brush").data([chart.data]);
	    },
	    insert: function() {
		chart.brush.clear();
		return this.append("g")
		    .attr("class", "brush");
	    },
	    events: {
		"merge": function() {
		    chart.brush = d3.svg.brush().x(chart.xScale).on("brushend", load_selection);
		    return this
			.call(chart.brush)
			.selectAll("rect")
			.attr("y", 0)
			.attr("height", chart._height);
		}
	    }
	    
	});
    }
});

d3.chart("H1DSEditModeChart", {
    initialize: function() {
	// resize bar width
	var rb_width = 15;
	//var background = this.base.append("g")
	//    .classed("graph-background", true);
	var chart = this;


	var resizebar_data = function(data) {
	    
	}

	this.layer("background", chart.base.append("g"), {
	    dataBind: function(data) {
		return this.selectAll("rect.background").data([data]);
	    },
	    insert: function() {
		return this.insert("rect")
		.attr("class", "background-edit")
		.attr("x", function(d) {return d.x0px;})
		.attr("y", function(d) {return d.y1px;})
		.attr("width", function(d) {return d.x1px-d.x0px;})
		.attr("height", function(d) {return d.y0px - d.y1px;});
	    }
	    
	});

	// rb_x (rb_y) classes are to identify which attibute should be modified by mouse events
	var resizebar_data = function(d) {
	    var rb_length = d.x1px - d.x0px - 2*rb_width;
	    var rb_height = d.y0px - d.y1px - 2*rb_width;
	    return [
		// edges
		{'x': d.x0px,
		 'y': d.y1px + rb_width,
		 'width': rb_width,
		 'height': rb_height,
		 'class': "resizebar edge rb_x"
		},
		{'x': d.x1px-rb_width,
		 'y': d.y1px + rb_width,
		 'width': rb_width,
		 'height': rb_height,
		 'class': "resizebar edge rb_x"
		},
		{'x': d.x0px+rb_width,
		 'y': d.y1px,
		 'width': rb_length,
		 'height': rb_width,
		 'class': "resizebar edge rb_y"
		},
		{'x': d.x0px+rb_width,
		 'y': d.y0px-rb_width,
		 'width': rb_length,
		 'height': rb_width,
		 'class': "resizebar edge rb_y"
		},
		// corners
		{'x': d.x0px,
		 'y': d.y1px,
		 'width': rb_width,
		 'height': rb_width,
		 'class': "resizebar corner rb_x rb_y"
		},
		{'x': d.x1px-rb_width,
		 'y': d.y1px,
		 'width': rb_width,
		 'height': rb_width,
		 'class': "resizebar corner rb_x rb_y"
		},
		{'x': d.x0px,
		 'y': d.y0px-rb_width,
		 'width': rb_width,
		 'height': rb_width,
		 'class': "resizebar corner rb_x rb_y"
		},
		{'x': d.x1px-rb_width,
		 'y': d.y0px-rb_width,
		 'width': rb_width,
		 'height': rb_width,
		 'class': "resizebar corner rb_x rb_y"
		}
	    ];
	}


	this.layer("resizeedges", chart.base.append("g"), {
	    dataBind: function(data) {
		return this.selectAll("rect.resizebar ").data(resizebar_data(data));
	    },
	    events: {
		"enter": function() {
		    this.on("click", function() {console.log("xx events");})
		}
	    },
	    insert: function() {
		return this.insert("rect")
		.attr("class", function(d) {return d.class;})
		.attr("x", function(d) {return d.x;})
		.attr("y", function(d) {return d.y;})
		.attr("width", function(d) {return d.width;})
		.attr("height", function(d) {return d.height;})
	    }
	    
	});
    }
        
});



function updateCharts() {
    var pagelets = d3.selectAll("#h1ds-portlet-data div.portlet-content")
	.data(plotState.pagelets)
	.append("svg")
	.attr("width", function(d) {return d.width + d.margin.left + d.margin.right; })
	.attr("height", function(d) {return d.height + d.margin.top + d.margin.bottom; })
	.append("g")
	.attr("transform", function(d) {return "translate(" + d.margin.left + "," + d.margin.top + ")"});

    pagelets.each(function(d, i) {
	// calculate widths of rows and columns
	d.column_width = d.width/d.n_columns;
	d.row_height = d.height/d.n_rows;

	// generate scales to map pagelet grid to pixels.
	d.xScale = d3.scale.linear()
	    .domain([0, d.n_columns])
	    .range([0, d.width]);
	d.yScale = d3.scale.linear()
	    .domain([0, d.n_rows])
	    .range([d.height, 0]);

	// set up pagelet grid on which the charts are set.
	var pagelet_grid = d3.select(this).append("g").attr("class", "pagelet-grid");
	for (var j=0; j <= d.n_columns; j++) {
	    pagelet_grid
		.append("line")
		.attr("x1", function() {return Math.round(j*d.column_width)})
		.attr("x2", function() {return Math.round(j*d.column_width)})
		.attr("y1", 0)
		.attr("y2", d.height);
	}
	for (var j=0; j <= d.n_rows; j++) {
	    pagelet_grid
		.append("line")
		.attr("x1", 0)
		.attr("x2", d.width)
		.attr("y1", function() {return Math.round(j*d.row_height)})
		.attr("y2", function() {return Math.round(j*d.row_height)});
	}

	// update the chart locations in pixels (from pagelet grid coordinates).
	for (var j=0; j < d.charts.length; j++) {
	    d.charts[j].x0px = d.xScale(d.charts[j].x0);
	    d.charts[j].x1px = d.xScale(d.charts[j].x1);
	    d.charts[j].y0px = d.yScale(d.charts[j].y0);
	    d.charts[j].y1px = d.yScale(d.charts[j].y1);

	    if (plotState.settings.edit_mode == true) {
		var chart = d3.select(this).append("g")
		    .attr("transform", "translate(" + d.charts[j].x0px + "," + d.charts[j].y1px + ")")
		    .chart("H1DSEditModeChart");
		console.log(d.charts[j].x1px - d.charts[j].x0px);
		chart.width(d.charts[j].x1px - d.charts[j].x0px);
		chart.height(d.charts[j].y1px - d.charts[j].y0px);
		chart.draw(d.charts[j]);
		//d3.select("rect.resizebar").on("click", function(d,i) {return "test";});

	    } else {	    
		var chart = d3.select(this).append("g")
		    .attr("class", "chart")
		    .attr("transform", "translate(" + d.charts[j].x0px + "," + d.charts[j].y1px + ")")
		    .chart("H1DSTestChart");
		chart.width(d.charts[j].x1px - d.charts[j].x0px);
		chart.height(d.charts[j].y0px - d.charts[j].y1px);
		// TODO: fix the recurive datas before here!
		chart.draw([d.charts[j].data[0].data.data]);
	    }
	    
	}

    });

}

*/

////////////////////////////////////////////////////////////////////////
// Run code when DOM is ready
////////////////////////////////////////////////////////////////////////

// we maintain  the page state  in a single object  so we can  pass it
// around using the  HTML5 history API (i.e. change  plots and browser
// location  bar  without reloading  page,  making  sure browser  back
// button still works)

var plotState = {};

function datamap(data) {
};

function loadWorksheet() {
	// data = [plot_1, plot_2, plot_3, ..., plot_n]
	// plot_n = {plot_coords:[x0, y0, x1, y1],
	//           data = [series_1,series_2,..., series_n],
        //            }
	// series_n = {url: source_url,
	//             url_parser: function which returns object defined below}
	// url_parser: function(url, {dim_limits=[[dim0_min, dim0_max], [dim1_min, dim1_max],...], (other modifiers)})
	//             
	//             returns {
	//	        dimension: [dim1, dim2, ...],
	//	        dimension_dtype: str,
	//	        dimension_units: str,
	//	        metadata: {key1:val1, key2:val2, ...},
	//	        name: str,
	//	        value: [ch1, ch2, ...],
	//	        value_dype: str,
	//	        value_units: str,
	//	       }
    function url_parser(url, settings) {
	// TODO: allow for settings - zooming etc
	var new_uri = getRawUri(url, settings.width);
	if (settings.hasOwnProperty("min")) { // TODO - what if only min or max but not both?
	    new_uri.updateOrAddBaseFilter("dim_range", {'min':settings.min, 'max':settings.max});
	}

	var output;
	$.ajax({url: new_uri.renderExtraUri(),
		dataType: "json",
		async:false})
	    .done(function(a) {
		output = a.data;
	    });
	return output;
    }

    var test_data = [
	{'plot_coords':[0,0,10,10],
	 'modifiers':{},
	 'data':[{url:  window.location.toString(), url_parser: url_parser}
		]}
		    ];
    
    var worksheet = dataviewer.create("div.data.worksheet");
    worksheet.data(test_data);
    worksheet.draw();
    
    }



$(document).ready(function() {

    // Scroll past the  header so there is more space  for viewing data,
    // especially helps usability on mobile devices.

    $('#main').scrollView();
    
    // For summary database, poll server for new shots.
    // TODO: use SSE instead of short polling!!

    autoPollSummaryDB();

    // Load cookie to arrange portlets, etc.

    loadCookie();

    // load the state info 

    loadWorksheet();

    // update pagelets

    //updatePagelets();

    // REMOVEPopulate the data pagelets.

    //$(".h1ds-pagelet").each(function() {
    //populatePagelet($(this), window.location.toString());
    //});
});

