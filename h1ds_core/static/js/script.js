// Custom javascript code for H1 data system
// David Pretty, 2010-2012

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
/*
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
*/

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


/*
 * getPlotQueryString
 *
 * Generate a URL query string for filtered data.
 *
 * arguments: any number of [filter_number, filter_name, arg1, arg2,...]
 * returns: current URL with query string generated from filters.
 *
 * Example:
 *     getPlotURL(['1','filter_a','10','20'], ['999','filter_b'])
 * returns:
 *   ?(current query string)&f1_name=filter_a&f1_arg0=10&f1_arg1=20&\
 *   f999_name=filter_b&view=json
 *
 */
function getPlotQueryString() {
    // If the current URL has a query string, then we append to to ('&')
    // otherwise we create it '?'.
    var plot_url = window.location.search + (window.location.search.length ? '&' : '?');

    for (var i=0; i < arguments.length; i++) {
	if (i>0) plot_url += '&';
	plot_url += 'f'+arguments[i][0]+'_name='+arguments[i][1];
	for (var j=2; j< arguments[i].length; j++) {
	    plot_url += '&f'+arguments[i][0]+'_arg'+(j-2)+'='+arguments[i][j];
	}
    }
    
    return (plot_url += '&view=json');
}

/*
 * Interactive data plots for MDSplus.
 * 
 * There  are  three   primary  objects:  PlotContainer,  PlotSet  and
 * Plot1D. PlotContainer  is called first,  it inserts an  SVG element
 * inside   the   DOM   element   whose  id   matches   the   supplied
 * argument. PlotSet  is a  container for a  set plots using  the same
 * dataset; e.g. timeseries and  power spectrum. Plot1D is used inside
 * a PlotSet and does the actual plotting of data.
 *
 *
 *
 */


/* 
 * PlotContainer 
 * 
 * Set up SVG container for plots inside HTML element.
 * 
 * arguments: id of HTML element for container.
 *
 *  +-------#id------------------------------------------------------+
 *  |                                                                |
 *  | +-----svg---------------------------------------------------+  |
 *  | |                                                           |  |
 *  | |   +---g.plotset---------------------------------------+   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   +---------------------------------------------------+   |  |
 *  | |                  ^                                        |  |
 *  | |                  |  plotset_spacing                       |  |
 *  | |                  v                                        |  |
 *  | |   +---g.plotset---------------------------------------+   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   +---------------------------------------------------+   |  |
 *  | |                                                           |  |
 *  | |                                                           |  |
 *  | |                                                           |  |
 *  | |   +---g.plotset---------------------------------------+   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   |                                                   |   |  |
 *  | |   +---------------------------------------------------+   |  |
 *  | |                                                           |  |
 *  | +-----------------------------------------------------------+  |
 *  |                                                                |
 *  | +---<p>-----------------------------------------------------+  |
 *  | |                                                           |  |
 *  | | Enter URL to add another...                               |  |
 *  | |                                                           |  |
 *  | +-----------------------------------------------------------+  |
 *  |                                                                |
 *  +----------------------------------------------------------------+
 *
 */

function PlotContainer(id) {
    var that = this;
    this.id = id;
    var container = d3.select(id);
    this.svg = container.append("svg:svg");
    
    // spacing between plotsets
    this.plotset_spacing = 10;

    // array of plotset instances in this container
    this.plotsets = [];

    // append a form entry box (after SVG) to add URL for new plot
    container.append("p").text("Enter data URL to add another plot");
    container.append("form")
	.attr("id","add-plot-form")
	.html('<input id="add-plot-url" type="text" /><input type="submit" />');    
    $("#add-plot-form").submit(
	function() {that.addPlotSet(
	    (function() {return 'test_'+that.plotsets.length})(),
	    $("#add-plot-url").val()); return false;}
    );

}



PlotContainer.prototype.resetHeight = function() {
    // calculate the vertical translation for the plotset
    var new_height = 0;
    this.plotsets[0].offset = new_height;
    for (var i=1; i<this.plotsets.length; i++) {
	//new_height += this.plotsets[i-1].offset;
	new_height += this.plotsets[i-1].getHeight();
	new_height += this.plotset_spacing;	
	this.plotsets[i].offset = new_height;
    }

    new_height += this.plotset_spacing;
    new_height += this.plotsets[this.plotsets.length-1].getHeight();
    

    // adjust the height of plot container (SVG) and DOM container element.
    this.svg.attr("height",new_height);
    $(this.id).height(new_height);

    this.svg.selectAll("g.plotset")
	.data(this.plotsets)
	.attr("transform", function(d) {return "translate(0,"+d.offset+")"});


};

PlotContainer.prototype.addPlotSet = function(plotset_name, data_url, plot_type) {

    var new_plotset = new PlotSet(plotset_name, data_url);
    new_plotset.container = this;
    // add new plotset to the plot container
    this.plotsets.push(new_plotset);
    this.resetHeight();

    // Bind plotsets and load data. Each plotset is wrapped by an <svg:g> element.
    this.svg.selectAll("g.plotset")
	.data(this.plotsets)
	.enter().append("svg:g")
	.attr("transform", function(d) {return "translate(0,"+d.offset+")"})
	.attr("class","plotset")
	.attr("id", function(d) { return "plotset-"+d.name;})
	.call(function(a) { 
	    a.datum().g = a;
	    a.datum().loadData(); 
	});
};

/* 
 * PlotSet
 *
 * Wrapper for individual plots using same data.  
 *
 * mp = menu_padding. note mp[2] is ignored (height of menu stretched
 * to fit number of buttons.
 *
 *
 *  +---g.plotset----------------------------------------------------+
 *  |                ^                                       ^       |
 *  |                | padding[0]                            | mp[0] |
 *  |                v                                       v       |
 *  |      +---g.plot----------------------------------+    +--+     |
 *  |<---->|                                           |    |  |     |
 *  |  p   |                                      mp[3]|<-->|  |<--->|
 *  |  a   |                                           |    |  |mp[1]|
 *  |  d   +----------------------------------------- -+    |  |     |
 *  |  d           ^                                        |  |     |
 *  |  i           | plot_spacing                           |  |     |
 *  |  n           v                                        +--+     |
 *  |  g   +---g.plot----------------------------------+             |
 *  | [3]  |                                           |             |
 *  |      |                                           |             |
 *  |      |                                           |             |
 *  |      +-------------------------------------------+             |
 *  |                                                                |
 *  |      +---g.plot----------------------------------+             |
 *  |      |                                           |             |
 *  |      |                                           |<----------->|
 *  |      |                                           |  padding[1] |
 *  |      +-------------------------------------------+             |
 *  |          ^                                                     |
 *  |          | padding[2]                                          |
 *  |          v                                                     |
 *  +----------------------------------------------------------------+
 *
 */

function PlotSet(plotset_name, data_url) {
    var that = this;
    this.name = plotset_name;
    this.data_urls = [data_url];
    // zoom to brush - if the brush is resized, should the axes limits be reset to 
    // brush limits (zoom).
    this.plots = {'main':{'height':400, 'instance':null, 'zoom_to_brush':true},
		  'overview':{'height':200, 'instance':null, 'zoom_to_brush':false},
		  'powerspectrum':{'height':200, 'instance':null, 'zoom_to_brush':false},
		 };
    this.active_plots = ['main'];
    this.plot_spacing = 10;
    this.padding = [5,50,5,5];
    this.width = 10;
    this.menu_padding = [10,5,10,5];
    this.data_colours = ['#010101', '#ED2D2E', '#008C47', '#1859A9', '#662C91', '#A11D20'];

    this.addSignalDialog = $('<div></div>')
	.html('<p class="validateTips">Enter URL for new signal</p><form><fieldset><label for="url">URL</label><input type="text" name="url" id="signalurl" class="text ui-widget-content ui-corner-all"/></fieldset></form>')
	.dialog({
	    autoOpen:false,
	    title: 'Add signal',
	    buttons: {
		"add signal": function() {
		    var isValid = true;
		    var newURL = $('#signalurl').val();
		    $('#signalurl').removeClass("ui-state-error");
		    $(".validateTips").removeClass("ui-state-highlight");
		    $(".validateTips").text("Enter URL for new signal.");
		    for (var i=0; i<that.data_urls.length;i++) {
			if (newURL === that.data_urls[i]) {
			    isValid = false;
			}
		    }
		    if (isValid) {
			that.data_urls.push(newURL);
			that.loadData();
			$('#signalurl').val("");
			$(this).dialog("close");
		    } else {
			$("#signalurl").addClass("ui-state-error");
			$(".validateTips").addClass("ui-state-highlight");
			$(".validateTips").text("URL already plotted. Choose another one.");
		    }
		}
	    },
	}).submit(function (e) { return false; });

}

PlotSet.prototype.getHeight = function() {
    var h = 0;
    for (var i=0; i < this.active_plots.length; i++) {
	h += this.plots[this.active_plots[i]].height;
    }
    if (this.active_plots.length > 1) {
	h += (this.active_plots.length-1)*this.plot_spacing;
    }
    return h;
};

PlotSet.prototype.setWidth = function(new_width) {
    this.width = new_width;
};

PlotSet.prototype.loadData = function() {

    this.setWidth($(this.g).parent().width());
    
    var that = this;
    // generate a dataset with instances of active plots
    var plotlist = [];
    var offset = 0;
    for (var i=0; i<this.active_plots.length; i++) {
	// if we don't have an active instance, then make one.
	if (!this.plots[this.active_plots[i]].instance) {
	    this.plots[this.active_plots[i]].instance = new Plot1D(this.name+"-"+this.active_plots[i],
								   this.plots[this.active_plots[i]].height,
								   this.width-this.padding[1]-this.padding[3],
								   this.plots[this.active_plots[i]].zoom_to_brush
								  )
	}
	offset += this.plots[this.active_plots[i]].height;
	this.plots[this.active_plots[i]].instance.offset = offset;
	this.plots[this.active_plots[i]].instance.plotset = this;
	plotlist.push(this.plots[this.active_plots[i]].instance);
	offset += this.plot_spacing;
    }

    this.g.selectAll("g.plot")
	.data(plotlist)
	.enter().append("svg:g")
	.attr("transform", function(d) { return "translate("+that.padding[3]+","+(d.offset+that.padding[0])+")" })
	.attr("class","plot")
	.attr("id", function(d) { return "plot-"+that.name+'-'+d.name;});

    this.g.selectAll("g.plot")
	.data(plotlist)
	.exit().remove();

    this.g.selectAll("g.plot").each( function(d,i) { d.g = d3.select(this); d.loadData(); });
    
    this.loadMenu();
    this.container.resetHeight();

};

PlotSet.prototype.loadMenu = function() {
    // button padding
    var bp = 5;
    // button width
    var bw = this.padding[1]-this.menu_padding[1]-this.menu_padding[3]-2*bp;
    // button height
    var bh = this.padding[1]-this.menu_padding[1]-this.menu_padding[3]-2*bp;
    var nButtons = 2;
    var that = this;
    var pm = this.g.selectAll(".plot-menu");
    if (pm[0].length === 0) {
	this.g.append("g").attr("class", "plot-menu")
	    .attr("transform", "translate("+
		  (this.width-this.padding[1]+this.menu_padding[3])+
		  ","+(this.menu_padding[0])+")")
	    .append("rect")
	    .attr("width", (this.padding[1]-this.menu_padding[1]-this.menu_padding[3]))
	    .attr("height", 2*bp+nButtons*bh+(nButtons-1)*bp);
	// add buttons
	var pm = this.g.select(".plot-menu");
	
	// button for adding another signal from URL
	pm.append("g")
	    .attr("class", "button addplot")
	    .attr("transform", "translate("+bp+","+bp+")")
	    .on("click", function(d,i) { that.addSignalDialog.dialog('open'); return false;} )
	    .append("rect")
	    .attr("width", bw)
	    .attr("height", bh);
	pm.selectAll('g.button.addplot')
	    .append("path")
	    .attr("d", "M"+0+" "+(0.7*bh)	// add signal icon
		  +" L"+(0.2*bw)+" "+(0.7*bh)
		  +" L"+(0.3*bw)+" "+(0.6*bh)
		  +" L"+(0.4*bw)+" "+(0.8*bh)
		  +" L"+(0.5*bw)+" "+(0.6*bh)
		  +" L"+(0.6*bw)+" "+(0.8*bh)
		  +" L"+(0.7*bw)+" "+(0.6*bh)
		  +" L"+(0.8*bw)+" "+(0.7*bh)
		  +" L"+(1.0*bw)+" "+(0.7*bh)
		  +" M"+(0.7*bw)+" "+(0.1*bh)
		  +" L"+(0.7*bw)+" "+(0.3*bh)
		  +" M"+(0.6*bw)+" "+(0.2*bh)
		  +" L"+(0.8*bw)+" "+(0.2*bh)
		 );

	// button for adding overview plot
	pm.append("g")
	    .attr("class", "button toggleoverview")
	    .attr("transform", "translate("+bp+","+(2*bp+bh)+")")
	    .on("click", function(d,i) { that.toggleOverview(); return false;} )
	    .append("rect")
	    .attr("width", bw)
	    .attr("height", bh);

	pm.selectAll('g.button.toggleoverview')
	    .append("text")
	    .attr("y", 0.4*bh)
	    .attr("textLength", bw)
	    .text("OVER");
	pm.selectAll('g.button.toggleoverview')
	    .append("text")
	    .attr("y", 0.9*bh)
	    .attr("textLength", bw)
	    .text("VIEW");
    }
};

PlotSet.prototype.toggleOverview = function() {
    var plotName = "overview";
    // check if we have overview.
    var isActive = ($.inArray(plotName, this.active_plots) !== -1);
    var toggleButton = this.g.select("g.button.toggleoverview");
    toggleButton.classed("active", !isActive);
    if (isActive) {
	this.active_plots.splice( $.inArray(plotName, this.active_plots), 1 );
    } else {
	this.active_plots.push(plotName);
    }
    this.loadData();
}

/*
 * Plot1D
 *
 * Setup axes etc, for one or more Signals.
 * Corresponds to an SVG <g> container.
 *
 * arguments: name of plot, data URL
 * 
 *
 * the menu  padding is  relative to  the gap in  the right  hand plot
 * padding so the width of  the menu is padding[1] - menu_padding[1] -
 * menu_padding[3]  i.e.  make sure  padding[1]  > (menu_padding[1]  +
 * menu_padding[3])  note: menu_padding[2]  is currently  ignored. the
 * height  of  the  menu   is  adjusted  dynamically  as  buttons  are
 * added. Note  that the svg:g  container doesn't have fixed  width or
 * height, but does have translated coordinates.
 *
 * TODO:
 * -- the   unique  data   names   should  really   be  maintined   by
 * PlotSet. It's simpler  for now just to manage  withing Plot1D as we
 * need  the MDS  path names  returned from  the call  to  the server.
 * Perhaps PlotSet  should manage server  calls?  This should  work if
 * all plots  in a  PlotSet are  the same width,  so we  can determine
 * sampling at the PlotSet level.
 *
 * 
 * +--g.plotset-------------------------------------------+
 * |                                                      |
 * |  +-----g.plot--#plot-plotname---------------------+  |
 * |  |  ^                 ^                           |  |
 * |  |<-+--width----------+-------------------------->|  |
 * |  |  |                 v padding[0]                |  |
 * |  |  |  +---------------------------+              |  |
 * |  |  |  |                           |<-padding[1]->|  |
 * |  |  |  |                           |              |  |
 * |  |  h  |                           |              |  |
 * |  |  e  |                           |              |  |
 * |  |  i  |                           |              |  |
 * |  |  g  |                           |              |  |
 * |  |  h  |                           |              |  |
 * |  |  t  |                           |              |  |
 * |  |  |  |                           |              |  |
 * |  |< +->|padding[3]                 |              |  |
 * |  |  |  +---------------------------+              |  |
 * |  |  |                 ^                           |  |
 * |  |  |                 | padding[2]                |  |
 * |  |  v                 v                           |  |
 * |  +------------------------------------------------+  | 
 * |                                                      | 
 * |  +-----g.plot---#plot-nextplot--------------------+  |
 * |  |                                                |  |
 * |  | etc...                                         |  |
 * |  |                                                |  |
 * +------------------------------------------------------+
 * 
 * 
 */

function Plot1D(name, height, width) {
    this.name = name;
    this.data_names = [];
    this.padding = [5,5,40,40];
    // height of plot, including padding
    this.height = height;
    // width of plot, including padding. 
    this.width = width;
    // if  true, show  overview  plot beneath  main  plot. useful  for
    // context when zooming and panning.
    this.overview = false;

    this.data = [];
    this.xlim = [Number.MAX_VALUE,-Number.MAX_VALUE];
    this.ylim = [Number.MAX_VALUE,-Number.MAX_VALUE];
    // how much extra space to plot on y-axis so the data doesn't go
    // right to the edge.
    this.range_padding = 0.05;
    this.x = d3.scale.linear().range(
	[this.padding[3], this.width - this.padding[1]]
    );
    this.y = d3.scale.linear().range(
	[this.height-this.padding[0]-this.padding[2],0]
    );
    this.xAxis = d3.svg.axis().scale(this.x).tickSize(-(this.height-this.padding[0]-this.padding[2]));
    this.yAxis = d3.svg.axis().scale(this.y).orient("left").tickSize(-(this.width-this.padding[3]-this.padding[1]));

}

Plot1D.prototype.setWidth = function(width) {
    this.width = width;
    this.x.range(
	[0, this.width - this.padding[1]-this.padding[3]]
	);
    this.yAxis.tickSize(-(this.width-this.padding[3]-this.padding[1]));
    
};

// update x and y axes limits
Plot1D.prototype.updateAxes = function() {
    var that=this;
    for (var i=0; i<this.data.length; i++) {
	this.data[i].min_data = this.data[i].is_minmax ? d3.min(this.data[i].data[0]) : d3.min(this.data[i].data);
	this.data[i].max_data = this.data[i].is_minmax ? d3.max(this.data[i].data[1]) : d3.max(this.data[i].data);


	// get min and max values for axes
	this.data[i].delta_data = this.data[i].max_data - this.data[i].min_data;
	this.data[i].min_plot = this.data[i].min_data - this.range_padding*this.data[i].delta_data;
	this.data[i].max_plot = this.data[i].max_data + this.range_padding*this.data[i].delta_data;
	
	// get min and max dimension (i.e. x axis, e.g. time)
	this.data[i].min_dim = this.data[i].dim[0];
	this.data[i].max_dim = this.data[i].dim[this.data[i].dim.length-1];

	// update plot x,y lims
	this.xlim[0] = d3.min([this.xlim[0], this.data[i].min_dim]);
	this.xlim[1] = d3.max([this.xlim[1], this.data[i].max_dim]);
	this.ylim[0] = d3.min([this.ylim[0], this.data[i].min_plot]);
	this.ylim[1] = d3.max([this.ylim[1], this.data[i].max_plot]);
    }
    this.x.domain(this.xlim);
    this.y.domain(this.ylim);
    var t = this.g.transition().duration(500);
    t.select(".y.axis").call(this.yAxis);
    t.select(".x.axis").call(this.xAxis);
    t.selectAll("path.data").attr("d", function(d,i) { return that.formatData(d,i); });

    
    
};

Plot1D.prototype.loadData = function() {
    this.data = [];
    for (i=0; i<this.plotset.data_urls.length; i++) {
	this.loadURL(this.plotset.data_urls[i]);
    }
    this.updateDataNames();
    this.updateAxes();
    this.displayData();
};

// Generate unique names for plots based on MDS paths.
// TODO: need to include H1DS filters in here also.
Plot1D.prototype.updateDataNames = function() { 
    // split the components of the MDS path we want to compare

    var split_names = [];
    for (var i=0; i<this.data.length; i++) {
	split_names.push(
	    this.data[i].meta['mds_path'].replace(/::/g,':').replace(/:/g,'.').split('.')
	);
    }

    // if there is only one signal, return the last path component as the name
    if (split_names.length === 1) {
	this.data_names[0] = this.data[0].meta['mds_shot']+" "+split_names[0][split_names[0].length-1];
	return true;
    }


    // otherwise iterate through path components and ignore the common components
    
    var shortest_path = Number.MAX_VALUE;
    for (var i=0; i<split_names.length;i++) {
	if (split_names[i].length < shortest_path ) shortest_path = split_names[i].length;
    }

    var common_level = 0;
    var different_level = false;
    for (var i=0; i<shortest_path; i++) {
	for (var j=1; j<split_names.length;j++) {
	    if (split_names[j][i] !== split_names[0][i]) different_level=true;
	}
	if (different_level) break;
	common_level++;
    }

    for (var i=0; i<split_names.length; i++) {
	this.data_names[i] = this.data[i].meta['mds_shot'] + " ";
	for (var j=common_level; j<split_names[i].length-1; j++) {
	    this.data_names[i] += split_names[i][j];
	    this.data_names[i] += '.';
	}
	this.data_names[i] += split_names[i][split_names[i].length-1];
    }
};

Plot1D.prototype.loadURL = function(data_url) {
    var that = this;
    // does data_url contain a query string?
    var query_char = data_url.match(/\?.+/) ? '&' : '?';
    data_url += (query_char+'f999_name=resample_minmax&f999_arg0='+(this.width-this.padding[1]-this.padding[3])+'&view=json');
    // TODO: we should be able to easily inspect returned data to see
    // if it is minmax, rather than needing a dedicated js function
    $.ajax({url: data_url, 
	    dataType: "json",
	    async:false})
	.done(function(a) {
	    a.is_minmax = isMinMaxPlot(a);
	    that.data.push(a);
	});
};


// format data for SVG <path> element's d attribute.
Plot1D.prototype.formatData = function(d, i) {
    var that = this;
    if (d.is_minmax) {
	var fill_data = fillPlot(d);
	var line = d3.svg.line()
	    .x(function(a) { return that.x(a[0]); })
	    .y(function(a) { return that.y(a[1]); });
	return line(fill_data);
    } else {
	var line = d3.svg.line()
	    .x(function(a,j) { return that.x(d.dim[j]); })
	    .y(function(a) { return that.y(a); });
	return line(d.data);
    }
};


Plot1D.prototype.displayData = function() {
    var that=this;

    // only display x axis if it doesn't already exist
    var xa = this.g.selectAll(".axis.x");
    if (xa[0].length === 0) {
	this.g.append("svg:g").attr("class","x axis")
	    .attr("transform", "translate(0,"+-(this.padding[2])+")")
	    .call(this.xAxis);
	this.g.select(".axis.x").append("text").attr("class", "x label")
	    .attr("x", 0.5*(this.width-this.padding[1]-this.padding[3]))
	    .attr("y", "2.5em")
	    .text(that.data[0].dim_units);

	// shift label to centre. 
	var xa_sel = "#" + this.g.attr("id") + " > g.x.axis > text.x.label";
	var new_x = $(xa_sel).attr("x") - $(xa_sel).width()/2 ;
	$(xa_sel).attr("x",new_x);
    }
    

    var ya = this.g.selectAll(".axis.y");
    if (ya[0].length === 0) {
	this.g.append("svg:g").attr("class","y axis")
	    .attr("transform", "translate("+this.padding[3]+","+-(this.height - this.padding[0])+")")
	    .call(this.yAxis);
	this.g.select(".axis.y").append("text").attr("class", "y label")
	    .attr("transform", "rotate(-90)")
	    .attr("x", -(this.height-this.padding[0]-this.padding[2])*0.5)
	    .attr("y", "-3em")
	    .text(that.data[0].data_units);

	// shift label to centre. 
	var ya_sel = "#" + this.g.attr("id") + " > g.y.axis > text.y.label";
	var new_y = $(ya_sel).attr("x") - $(ya_sel).width()/2 ;
	$(ya_sel).attr("x",new_y);

    }

    // for each data, add an SVD path element with the data.
    this.cell = this.g.append("g")
    	.attr("transform", "translate(0,"+-(this.height-this.padding[0])+")")
	.attr("class", "cell");

    this.cell.selectAll("path.data")
	.data(this.data)
	.enter().append("path")
	.attr("class","data")
	.classed("path-filled", function(d) { return d.is_minmax })
	.attr("d", function(d,i) { return that.formatData(d,i) })
	.style("stroke", function(d,i) { return that.plotset.data_colours[i]; })
	.style("fill", function(d,i) { return that.plotset.data_colours[i]; });


    this.drawLegend();
    
}; 

Plot1D.prototype.drawLegend = function() {
    var that=this;
    this.g.selectAll("g.legend").remove();
    this.g.selectAll("g.legend")
	.data(this.data_names)
	.enter().append("svg:g")
    	.attr("transform", function(d,i) { return "translate("+(that.padding[3]+10)+","+-(that.height - that.padding[0] - (i+1)*12)+")"; })
	.attr("class", "legend")
	.append("text")
	.text(function(d) {return d})
    	.style("fill", function(d,i) { return that.plotset.data_colours[i]; });

};


//
// plotSignal1D -- DEPRICATED - will be removed once the plotcontainer, etc
// above is complete.
//
//
// For a given  container div, we fetch data subsampled  to the width of
// the plot window.  The heights  of the plots are fixed.  Several plots
// are actally displayed.  A large plot which allows  zooming (TODO: and
// panning), and  a smaller (smaller  height) plot which shows  the full
// signal and highlights the region shown in the larger plot.  An FFT of
// the signal in the large plot is also shown.  TODO: Allow both panning
// and  zooming  of  plot  TODO:  more  usable FFT  plots,  maybe  a  2D
// spectrogram plot, which is selectable and applies filters to the freq
// range selected.
function plotSignal1D(id) {
    // Get margins and plot width  for container, so we can resample the
    // data to fit the window width.
    var width_data = getPlotWidth(id);

    // compile the URL for retrieving subsampled data
    var trace_query = getPlotQueryString([999, 'resample_minmax', width_data.plot]);
    
    // spacing between bottom of plot and container.
    // TODO: should merge this with getPlotWidth to have a single
    // function which provides margins.
    var bottom_spacing = 20;

    // height of the signal plot 
    var signal_height = 200, overview_height = 100;


    // this is a bit convoluted, get the data, pass if to getFourier, which passes it to dataReady.
    // getFourier doesn't actually use the data which it takes as an argument! just passes it along.
    // TODO: refactor so it is more easily understandable.
    var test_data = [];
    $.getJSON(trace_query, function(d){ test_data[0] = d;})
    $.getJSON(trace_query, getFourier);

    function getFourier(d) {
	// compile the URL to get power spectrum data.
	var fourier_query = getPlotQueryString([990, 'power_spectrum'], 
					       [995, 'norm_dim_range',0.0, 0.5],
					       [999, 'resample_minmax',width_data.plot]);
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
	    var new_data_url = getPlotQueryString([990, 'dim_range', s[0], s[1]],
						  [999,'resample_minmax',width_data.plot]);

	    function updateFourier(d) {
		var fourier_query = getPlotQueryString([980, 'dim_range', s[0], s[1]], 
						       [990, 'power_spectrum'], 
						       [995, 'norm_dim_range', 0.0,0.5], 
						       [999, 'resample_minmax', width_data.plot]);
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
	var pc = new PlotContainer("#signal-1d-placeholder");
	pc.addPlotSet('default', window.location.toString());
    }
    if ($("#signal-2d-placeholder").length) {
	plotSignal2D();
    }
    if ($("#signal-3d-placeholder").length) {
	data = plotSignal3D();
    }

});


