// Custom javascript code for H1 data system
// David Pretty, 2010


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
       //console.log(data);
       if (data.sigmin == undefined) {
       var d = Array(data.node_data.length);
       for( i=0; i < d.length; i++){
         d[i]=[data.node_dim[i],data.node_data[i]];
     }
       var dataset = [{data:d, color:"rgb(50,50,255)"}];
       return dataset;
}
       var d = {"signalmin":{"data": Array(data.sigmin.node_data.length)},
                "signalmax":{"data": Array(data.sigmax.node_data.length)}};
       for( i=0; i < d.signalmin.data.length; i++){
         d.signalmin.data[i]=[data.sigmin.node_dim[i],data.sigmin.node_data[i]];
         d.signalmax.data[i]=[data.sigmax.node_dim[i],data.sigmax.node_data[i]];
     }
     var dataset = [{id: 'sigmin', data:d.signalmin.data, lines:{show:true, lineWidth:0.3, fill:false, shadowSize:0}, color:"rgba(50,50,255,0.5)"},
		     {id: 'sigmax', data:d.signalmax.data, lines:{show:true, lineWidth:0.3, fill:0.5, shadowSize:0}, color:"rgba(50,50,255,0.5)", fillBetween: 'sigmin'}];
     return dataset;
} // end formatDataForPlots

function plotSignals() {
  var original_query = {{ request_query|safe }};
  var new_query = $.extend({}, original_query, {'view':'json', 'f999_ResampleMinMax':600})
  $.get(
    '',new_query,
     function (data) {
       var dataset = formatDataForPlots(data);
     var options = {selection:{mode:"x"}};
     var sigplot = $.plot($("#signal-placeholder"),  dataset, options  );
     var overviewplot = $.plot($("#signal-overview"),  dataset , options  );

     $("#signal-placeholder").bind("plotselected", function (event, ranges) {
        // do the zooming
        var new_query = $.extend({}, original_query, {'view':'json', 'f980_DimRange':ranges.xaxis.from+'_'+ranges.xaxis.to, 'f990_ResampleMinMax':300});
        //console.log(new_url);
        $.get('', new_query, function(newdata) {
        var new_d = formatDataForPlots(newdata);

        sigplot = $.plot($("#signal-placeholder"), new_d, options);

		     });
		     




        // don't fire event on the overview to prevent eternal loop
        overviewplot.setSelection(ranges, true);
    });
    
    $("#signal-overview").bind("plotselected", function (event, ranges) {
        sigplot.setSelection(ranges);
    });


     },
     'json'
  );
}


$(document).ready(function() {
    updateLatestShot();
    autoUpdateLatestShot();
    autoUpdateEvents();
    data = plotSignals();
    var shot=$('#mds-nav-shot').text();
    var tree=$('#mds-nav-treename').text();
    $(".mds-node-item").each(function() {
	populateMDSNav(tree, shot, $(this));
    });
});

 






















