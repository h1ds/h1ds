function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

// parseUri 1.2.2
// (c) Steven Levithan <stevenlevithan.com>
// MIT License

function parseUri (str) {
	var	o   = parseUri.options,
		m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
		uri = {},
		i   = 14;

	while (i--) uri[o.key[i]] = m[i] || "";

	uri[o.q.name] = {};
	uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
		if ($1) uri[o.q.name][$1] = $2;
	});

	return uri;
};

parseUri.options = {
	strictMode: false,
	key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
	q:   {
		name:   "queryKey",
		parser: /(?:^|&)([^&=]*)=?([^&]*)/g
	},
	parser: {
		strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
		loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
	}
};


// makeURI 1.2.2 - create a URI from an object specification; compatible with
//                 parseURI (http://blog.stevenlevithan.com/archives/parseuri)
// (c) Niall Smart <niallsmart.com>
// MIT License
function makeUri(u) {

    var uri = "";

    if (u.protocol) {
        uri += u.protocol + "://";
    }

    if (u.user) {
        uri += u.user
    }

    if (u.password) {
        uri += ":" + u.password
    }

    if (u.user || u.password) {
        uri += "@"
    }

    if (u.host) {
        uri += u.host
    }

    if (u.port) {
        uri += ":" + u.port
    }

    if (u.path) {
        uri += u.path
    }

    var qk = u.queryKey;
    var qs = [];

    for (k in qk) {

        if (!qk.hasOwnProperty(k)) {
            continue;
        }

        var v = encodeURIComponent(qk[k]);

        k = encodeURIComponent(k);

        if (v) {
            qs.push(k + "=" + v);
        } else {
            qs.push(k);
        }
    }

    if (qs.length > 0) {
        uri += "?" + qs.join("&")
    }

    if (u.anchor) {
        uri += "#" + u.anchor
    }

    return uri;
}

////////////////////////////////////////////////////////////////////////
// H1DSUri -  an object which  allows easy manipulation of  query string
// filters.
//
// TODO: H1DSUri stores the base_uri, and allows filters etc to be added
// - the base_uri should be what is in the browser window. The additional 
// filters are used in the presentation of the resource, fetched via ajax
// 
////////////////////////////////////////////////////////////////////////

function H1DSUri(base_uri) {

    this.base_uri = base_uri;
    this.base_uri_components = parseUri(base_uri);

    // extract h1ds filters from query strings
    this.base_h1ds_filters = [];
    this.base_non_h1ds_query = {};

    // extra query strings for visual display of data from base_uri
    // for example, subsample large data timeseries.
    this.extra_h1ds_filters = [];
    this.extra_non_h1ds_query = {};

    var tmp_h1ds_filters = {'fids':[]};
    var filter_re = /^f(\d+)(_(\w+))?/;

    for (var key in this.base_uri_components.queryKey) {
	if (this.base_uri_components.queryKey.hasOwnProperty(key)) {
	    var filter_info = filter_re.exec(key);
	    if (filter_info) {
		if (!tmp_h1ds_filters.hasOwnProperty(filter_info[1])) {
		    tmp_h1ds_filters.fids.push(filter_info[1]);
		    tmp_h1ds_filters[filter_info[1]] = {'name':"", "kwargs":{}, "fid":parseInt(filter_info[1])};
		}
		if (typeof filter_info[2] === 'undefined') {
		    tmp_h1ds_filters[filter_info[1]].name = this.base_uri_components.queryKey[key];
		}
		else {
		    tmp_h1ds_filters[filter_info[1]].kwargs[filter_info[3]] = this.base_uri_components.queryKey[key];
		}
	    }
	    else {
		this.base_non_h1ds_query[key] = this.base_uri_components.queryKey[key];
	    }
	}
    }
    for (var i=0; i<tmp_h1ds_filters.fids.length; i++) {
	this.base_h1ds_filters.push(tmp_h1ds_filters[tmp_h1ds_filters.fids[i]]);
    }
    
    this.sortH1DSFilters();

}

H1DSUri.prototype.sortH1DSFilters = function() {
    this.base_h1ds_filters = sortByKey(this.base_h1ds_filters, "fid");    
    this.extra_h1ds_filters = sortByKey(this.extra_h1ds_filters, "fid");    
}

H1DSUri.prototype.updateOrAddBaseFilter = function(name, kwargs) {
    // if the last base filter is the same as name, then we swap in the kwargs, otherwise append the kwargs on the end.
    var len = this.base_h1ds_filters.length;
    if (len>0 && this.base_h1ds_filters[len-1].name == name) {
	this.base_h1ds_filters[len-1].kwargs = kwargs;
    } else {
	this.addBaseFilter(name, kwargs);
    }
    
};

H1DSUri.prototype.shiftExtraH1DSFilterFIDs = function(delta) {
    for (var i=0; i<this.extra_h1ds_filters.length; i++) {
	this.extra_h1ds_filters[i].fid += delta;
    }
}

H1DSUri.prototype.shiftExtraFilterIDs = function() {
    // make sure the fids of extra filters all come after the base filter fids
    // if fid overlaps with extras, shift extra fids
    this.sortH1DSFilters();
    if (this.extra_h1ds_filters.length > 0) {
	var delta_fid = new_fid - this.extra_h1ds_filters[0].fid; 
	if (delta_fid >= 0) {
	    this.shiftExtraH1DSFilterFIDs(delta_fid+1);
	}
    }
    
}

H1DSUri.prototype.addBaseFilter = function(name, kwargs) {
    this.sortH1DSFilters();
    var len = this.base_h1ds_filters.length;
    if (len>0) {
	var new_fid = this.base_h1ds_filters[len-1].fid + 1;
    } else {
	var new_fid = 0;
    }
    this.base_h1ds_filters.push({"name":name, "kwargs":kwargs, "fid":new_fid});
    this.shiftExtraH1DSFilterFIDs(1);
}

H1DSUri.prototype.addExtraFilter = function(name, kwargs) {
    this.sortH1DSFilters();
    var len_extra = this.extra_h1ds_filters.length;
    var len_base = this.base_h1ds_filters.length;
    if (len_extra>0) {
	var new_fid = this.extra_h1ds_filters[len_extra-1].fid + 1;
    } else if (len_base>0) { 
	var new_fid = this.base_h1ds_filters[len_base-1].fid + 1;
    } else {
	var new_fid = 0;
    }
    this.extra_h1ds_filters.push({"name":name, "kwargs":kwargs, "fid":new_fid});
}

H1DSUri.prototype.packFilterIDs = function() {
    // TODO
    // renumber the filter ids so they are continuous from 0...

    console.log(this.extra_h1ds_filters);
};

H1DSUri.prototype.changeFilterID = function (oldID, newID) {
    // Check for the oldID name to avoid a ReferenceError in strict mode.
    
    for (var i=0; i<this.base_h1ds_filters.length; i++) {
	if (this.base_h1ds_filters[i].fid == parseInt(oldID)) {
	    this.base_h1ds_filters[i].fid = parseInt(newID);
	}
    }

    for (var i=0; i<this.extra_h1ds_filters.length; i++) {
	if (this.extra_h1ds_filters[i].fid == parseInt(oldID)) {
	    this.extra_h1ds_filters[i].fid = parseInt(newID);
	}
    }

    this.shiftExtraFilterIDs();
};


H1DSUri.prototype.renderBaseUri = function() {

    var newQueryKey = {};
    for (var key in this.base_non_h1ds_query) {
	if (this.base_non_h1ds_query.hasOwnProperty(key)) {
	    newQueryKey[key] = this.base_non_h1ds_query[key];
	}
    }

    for (var i=0; i<this.base_h1ds_filters.length; i++) {
	var fid = this.base_h1ds_filters[i].fid
	newQueryKey["f"+fid] = this.base_h1ds_filters[i].name;
	for (var fkey in this.base_h1ds_filters[i].kwargs) {
	    newQueryKey["f"+fid+"_"+fkey] = this.base_h1ds_filters[i].kwargs[fkey];
	}
    }

    var new_uri_components = jQuery.extend({}, this.base_uri_components);
    new_uri_components.queryKey = newQueryKey;
    return makeUri(new_uri_components);
};

H1DSUri.prototype.renderExtraUri = function() {
    var newQueryKey = {};
    for (var key in this.base_non_h1ds_query) {
	if (this.base_non_h1ds_query.hasOwnProperty(key)) {
	    newQueryKey[key] = this.base_non_h1ds_query[key];
	}
    }

    for (var i=0; i<this.base_h1ds_filters.length; i++) {
	var fid = this.base_h1ds_filters[i].fid
	newQueryKey["f"+fid] = this.base_h1ds_filters[i].name;
	for (var fkey in this.base_h1ds_filters[i].kwargs) {
	    newQueryKey["f"+fid+"_"+fkey] = this.base_h1ds_filters[i].kwargs[fkey];
	}
    }

    for (var key in this.extra_non_h1ds_query) {
	if (this.extra_non_h1ds_query.hasOwnProperty(key)) {
	    newQueryKey[key] = this.extra_non_h1ds_query[key];
	}
    }

    for (var i=0; i<this.extra_h1ds_filters.length; i++) {
	var fid = this.extra_h1ds_filters[i].fid
	newQueryKey["f"+fid] = this.extra_h1ds_filters[i].name;
	for (var fkey in this.extra_h1ds_filters[i].kwargs) {
	    newQueryKey["f"+fid+"_"+fkey] = this.extra_h1ds_filters[i].kwargs[fkey];
	}
    }

    var new_uri_components = jQuery.extend({}, this.base_uri_components);
    new_uri_components.queryKey = newQueryKey;
    return makeUri(new_uri_components);
};

H1DSUri.prototype.isBinary = function() {
    return (this.base_non_h1ds_query['format'] === 'bin') 
}

H1DSUri.prototype.getShot = function() {
    var path = this.uri_components.path;
    if (path[path.length-1] !== "/") {
	path = path+"/";
    }
    var tmp = path.match(/\/\d+\//);
    if (tmp===null) {
	return 0;
    } else {
	return Number(tmp[0].substring(1, tmp[0].length-1));
    }
}

H1DSUri.prototype.setShot = function(new_shot) {
    var path = this.uri_components.path;
    if (path[path.length-1] !== "/") {
	path = path+"/";
    }
    var new_path = path.replace(/\/\d+\//, "/"+new_shot+"/");
    this.uri_components.path = new_path;
}
