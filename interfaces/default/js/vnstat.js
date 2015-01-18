$(function () {
	ajaxload()
	get_currentspeed()
    setInterval(function () {
		get_currentspeed()
    }, 10000);

});

function makeArray(ary) {
	d = {}
	data = []
	dtx = []
	drx = []
	dt = []

	$.each(ary, function(i, a) {
		console.log(a)
		// all xml results are in kibi convert to gib
		var rx = parseInt(a.rx) / 1024 / 1024,
		tx = parseInt(a.tx) / 1024 / 1024;
		getReadableFileSizeString(tx)
		dtx.push(tx)
		drx.push(rx)
		dt.push((rx + tx))


	})
	d.dtx = dtx
	d.drx = drx
	d.dt = dt

	console.log("d")
	console.log(d)
	return d

}

function get_currentspeed() {
	$.get(WEBDIR + 'vnstat/tr', function(data) {
		if (data.rx && data.tx) {
			$("#vnstat-rx").text(data.rx);
			$("#vnstat-tx").text(data.tx);

		} else {
			return
		}

	})
}

// loads from db and makes html
function ajaxload() {
    $.ajax({
        url: WEBDIR + 'vnstat/dumpdb',
        async: false,
        success: function (data) {
        	t = $('.content')
        	console.log("ajaxload")
        	console.log("data.vnstat.interface")
        	console.log(data.vnstat.interface)
        	var interf = data["vnstat"]["interface"]
        	// check if its a dict or list
        	if (typeof(interf.id) !== 'undefined'){
        		var interf = [data["vnstat"]["interface"]]
        	}

            	$.each(interf, function (ii, dd) {

                    var p = $('<div>').addClass('row-fluid').attr('id', dd.id);
                    // w h needs to hardcoded in canvas
                    m = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'month_' + dd.id));
                    d = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'day_' + dd.id));
                    h = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'hour_' + dd.id));

                    // Inside m, d, h make a table or something for tab data

                    p.append(m);
                    p.append(d);
                    p.append(h);
                    t.append(p);

                });

			r = $('<div>').addClass("row-fluid").html('<div class="bwinfo"><span class="pull left">Bandwidth stats</span></h4><span class="pull-right bw_updated">x</span></div>')
			table = $('<table>').addClass("table").append("<tbody id='bandwidth_body'></tbody>")
			table.append()
			r.append(table)
			t.append(r)// some table stuff :P


        }

    });

    loaddb()
}


function loaddb() {
    $.ajax({
        url: WEBDIR + 'vnstat/dumpdb',
        async: false,
        success: function (data) {
        	var interf = data["vnstat"]["interface"]
        	if (typeof(data.vnstat["interface"].id) !== 'undefined'){
        		var interf = [data["vnstat"]["interface"]]
        	}

            $.each(interf, function (n, ainterf) {
                var z = ainterf;
                console.log("z");
                console.log(z);
                var interfaceid = z.id;
                var created = z.created.date;
                var date = moment(created.day + created.month + created.year, "DD.MM.YYYY").format('DD.MM.YYYY');

                var traffic = z.traffic;
                var months = traffic.months.month;
                var days = traffic.days.day;
                var hour = traffic.hours.hour;

                var twelve = makeArray(months);
                var dday = makeArray(days);
                var hour2 = makeArray(hour);

                makechart("month", interfaceid, twelve);
                makechart("day", interfaceid, dday);
                makechart("hour", interfaceid, hour2);


            });

        }
    });
}

function makechart(selector, interfaceid, d) {
	console.log("makechart")
	console.log(selector);
	console.log(d)
	if (selector == "day") {
		l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

	} else if (selector == "month") {
		l = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]

	} else if (selector == "hour") {
		l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
	}

	sel = selector + '_' + interfaceid
	var ctx = $('#' + sel).get(0).getContext("2d");
	parentwidth = $('#' + sel).parent().width()
	parentheight = $('#' + sel).parent().height()

	var data = {
		labels: l,

	    datasets: [
	        {

	            label: "Download",
	            fillColor: "rgba(220,220,220,0.2)",
	            strokeColor: "#56ff00",//"rgba(220,220,220,1)",
	            pointColor: "#56ff00",//"rgba(220,220,220,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(220,220,220,1)",
	            data: d.drx,
	            title: "Download",
	        },
	        {

	            label: "Upload",
	            fillColor: "rgba(151,187,205,0.2)",
	            strokeColor: "#0038ff",//"rgba(151,187,205,1)",
	            pointColor: "#0038ff",//"rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dtx,
	            title: "Upload",
	        },
	        {
	            label: "Total",
	            fillColor: "rgba(151,187,205,0.2)", // red #FF0000
	            strokeColor: "#EC7886", //rgba(151,187,205,1)",
	            pointColor: "#EC7886",//"rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dt,
	            title: "Total",
	        }
	    ]
	};
	// Would have been nice but to many datapoints
	//inGraphDataShow:true
	// annotateDisplay can cause problems, remove in that case.
	options = {showScale: true,
			inGraphDataShow: false,
	 		//scaleLabel: "<%=value%> GIB",
	 		graphTitle : selector,
	 		legend : true,
	 		responsive: true,
	 		annotateDisplay: true,
	 		yAxisUnit: "GIB",
	 		yAxisUnitFontSize: 11,
	 		//inGraphDataTmpl: "<%=v2.toFixed(2)%>",
	 		annotateLabel: "<%=(v1 == '' ? '' : v1) + (v1!='' && v2 !='' ? ' -  ' : '')+(v2 == '' ? '' : v2)+(v1!='' || v2 !='' ? ': ' : ' ') + v3.toFixed(2)%>",
		}
	new Chart(ctx).Line(data, options);
}

// grab form default.js instead? use math.pow
function getReadableFileSizeString(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);
    return fileSizeInBytes.toFixed(1) + byteUnits[i];
};