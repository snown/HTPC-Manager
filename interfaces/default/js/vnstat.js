// vnstats

// to test
/*
var data = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [
        {
            label: "Download",
            fillColor: "rgba(220,220,220,0.2)",
            strokeColor: "rgba(220,220,220,1)",
            pointColor: "rgba(220,220,220,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: [65, 59, 80, 81, 56, 55, 40]
        },
        {
            label: "Upload",
            fillColor: "rgba(151,187,205,0.2)",
            strokeColor: "rgba(151,187,205,1)",
            pointColor: "rgba(151,187,205,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(151,187,205,1)",
            data: [28, 48, 40, 19, 86, 27, 90]
        }
    ]
};
*/


$(document).ready(function(){
	//var piped;
	//loaddb2()
	//makeshittydivs();
	// Lets reduce the calls
	piped = loadstuff()
	//console.log("piped")
	//console.log(piped)
	// html must exist for chart draw
	//makeshittydivs(piped)
	//loaddb2(piped)
	loaddb2()
});

function loaddb() {
	$.getJSON(WEBDIR + 'vnstat/dump2', function(data) {
		//console.log(data);
		var interf = data.vnstat.interface
		var interfaceid = interf.id
		//console.log(interf)
		var created = interf.created.date
		//console.log(created);
		//var date = moment(created.year[0] + '-' + created.month[0] + '-' + created.day[0]).format('MMMM D, YYYY');
		//console.log(created.year, created.month, created.day)
		//var date2 = moment(created.year + created.month + created.day, "DD.MM.YYYY")
		var date = moment(created.day + created.month + created.year, "DD.MM.YYYY").format('DD.MM.YYYY')//.format('MMMM D, YYYY');
		//alert(date2)
		//alert(date);
		var traffic = interf.traffic;
		var months = traffic.months.month;
		var days = traffic.days.day;
		var hour = traffic.hours.hour;

		function makeArray(ary) {
			d = {}
			data = []
			dtx = []
			drx = []
			dt = []

			for (i = 0; i < ary.length; i++) {
				alert(ary[i].rx)
    			var rx = parseInt(ary[i].rx) * 1024,
			 	tx = parseInt(ary[i].tx) * 1024;
			 	dtx.push(tx)
			 	drx.push(rx)
			 	dt.push((rx + tx))
				//data.push[rx, tx, (rx + tx)]
			}
			d.dtx = dtx
			d.drx = drx
			d.dt = dt

			console.log("d")
			console.log(d)
			return d
		}

		function makeArrayDate(ary) {
			d = {}
			data = []
			dtx = []
			drx = []
			dt = []

			$.each(ary, function(i, a) {
				if (a.date.day == i) {
					// check if the days are correct
					/*
					var rx = parseInt(a.rx) * 1024,
			 		tx = parseInt(a.tx) * 1024;
			 		dtx.push(tx)
			 		drx.push(rx)
			 		dt.push((rx + tx))
			 		*/
				}
				var rx = parseInt(a.rx) * 1024,
			 		tx = parseInt(a.tx) * 1024;
			 		getReadableFileSizeString(tx)
			 		dtx.push(tx)
			 		drx.push(rx)
			 		dt.push((rx + tx))
				//console.log(a)
				//console.log(a.rx)
				//console.log(a.tx)


			})
			d.dtx = dtx
			d.drx = drx
			d.dt = dt

			console.log("d")
			console.log(d)
			return d

		}


		//var total = makeArray(traffic.total);
		//var thisMonth = makeArray(months[0]);
		$(".interface").text('@' + interfaceid)
		$(".updated").text(date)
		var twelve = makeArrayDate(months)
		var dday = makeArrayDate(days)
		var hour2 = makeArrayDate(hour)

		makechart("month", twelve)
		makechart("day", dday)
		makechart("hour", hour2)


	});
}

function makeArrayDate2(ary) {
	d = {}
	data = []
	dtx = []
	drx = []
	dt = []

	$.each(ary, function(i, a) {
		console.log("a");
		console.log(a);
		//if (a.date.day == i) {
					// check if the days are correct
					/*
					var rx = parseInt(a.rx) * 1024,
			 		tx = parseInt(a.tx) * 1024;
			 		dtx.push(tx)
			 		drx.push(rx)
			 		dt.push((rx + tx))
			 		*/
		//}
		var rx = parseInt(a.rx) * 1024,
		tx = parseInt(a.tx) * 1024;
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

function loadstuff() {
	$.getJSON(WEBDIR + 'vnstat/dump2', function (data) {
        var interf = data.vnstat.interface;
        // Check if there more interfaces if its a dict make array to loop it. Like the rest
        if (!interf.isArray) {
            interf = [[interf]];
        }
        //console.log("loadstuff")
        //console.log(interf)
        //piped = interf
        //return interf
        makeshittydivs(interf)
    });
}

// Use to make the html (needed for chart draw)
function makeshittydivs(data) {
	var ll = data
	console.log("makeshittydivs")
	console.log(data);
	t = $('.content')
	$.each(data, function(i, d) {
		//var p = $('<div>').addClass('row-fluid')
		$.each(d, function(ii, dd) {
			var p = $('<div>').addClass('row-fluid')
			// w h needs to hardcoded in canvas
			m = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'month_' + dd.id))
			d = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'day_' + dd.id))
			h = $('<div>').addClass("span4").append($('<canvas width=400px; height=400px">').attr('id', 'hour_' + dd.id))

			//m = $('<div>').addClass("t").append($('<canvas>').attr('id', 'month_' + dd.id))
			//d = $('<div>').addClass("t").append($('<canvas>').attr('id', 'day_' + dd.id))
			//h = $('<div>').addClass("t").append($('<canvas>').attr('id', 'hour_' + dd.id))

			p.append(m)
			p.append(d)
			p.append(h)
			t.append(p)


		})
		//t.append(p)
	})

	//loaddb2(ll)
}

function loaddb2(ll) {
	console.log("ll")
	console.log(ll)
	var data = $(ll)
    $.getJSON(WEBDIR + 'vnstat/dump2', function (data) {
        var interf = data.vnstat.interface;
        console.log("loaddb2, interf")
        console.log(typeof(interf))
        //var interf = ll;
        // Check if there more interfaces if its a dict make array to loop it. Like the rest
        if (!interf.isArray) {
            interf = [[interf]]; //try dump2
        }
        console.log("interf")
        console.log(interf)
        $.each(interf, function (n, ainterf) {
        	$.each(ainterf, function (n, z) {
	            var interfaceid = z.id;
	            var created = z.created.date;
	            var date = moment(created.day + created.month + created.year, "DD.MM.YYYY").format('DD.MM.YYYY');

	            var traffic = z.traffic;
	            var months = traffic.months.month;
	            var days = traffic.days.day;
	            var hour = traffic.hours.hour;

	            //$(".interface").text('@' + interfaceid);
	            //$(".updated").text(date);
	            var twelve = makeArrayDate2(months);
	            var dday = makeArrayDate2(days);
	            var hour2 = makeArrayDate2(hour);
	            rf = $("<div>").addClass(interfaceid + '_row')
	            // <canvas id="month" width="400" height="400"></canvas>
	            //var canv = $('<canvas/>',{'width':400,'height':400});
	            //rf.append($("<div>").addClass("span4").append(canv.attr('id', 'month_' + interfaceid)))
	            //rf.append($("<div>").addClass("span4").append(canv.attr('id', 'day_' + interfaceid)))
	            //rf.append($("<div>").addClass("span4").append(canv.attr('id', 'hour_' + interfaceid)))
	            makechart2("month", interfaceid, twelve)
	            makechart2("day", interfaceid, dday)
	            makechart2("hour", interfaceid, hour2)
	            //f.append(rf)

        	});

        });
    });
}

function makechart2(selector, interfaceid, d) {
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

	//var ctx = $("#month").get(0).getContext("2d");
	sel = selector + '_' + interfaceid
	//alert(sel);
	var ctx = $('#' + sel).get(0).getContext("2d");
	parentwidth = $('#' + sel).parent().width()
	parentheight = $('#' + sel).parent().height()

	var data = {
		labels: l,

	    //labels: ["January", "February", "March", "April", "May", "June",
		//		"July", "August", "September", "October", "November", "December" ],
	    datasets: [
	        {
	            label: "Download",
	            fillColor: "rgba(220,220,220,0.2)",
	            strokeColor: "rgba(220,220,220,1)",
	            pointColor: "rgba(220,220,220,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(220,220,220,1)",
	            data: d.drx//[65, 59, 80, 81, 56, 55, 40] // d.drx
	        },
	        {
	            label: "Upload",
	            fillColor: "rgba(151,187,205,0.2)",
	            strokeColor: "rgba(151,187,205,1)",
	            pointColor: "rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dtx//[28, 48, 40, 19, 86, 27, 90]
	        },
	        {
	            label: "Total",
	            fillColor: "rgba(151,187,205,0.2)",
	            strokeColor: "#EC7886", //rgba(151,187,205,1)",
	            pointColor: "rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dt//[28, 48, 40, 19, 86, 27, 90]
	        }
	    ]
	};
	//options = {scaleOverride : true}
	options = {}
	new Chart(ctx).Line(data, options);
	//gg.update()
}

function makechart(selector, d) {
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

	//var ctx = $("#month").get(0).getContext("2d");
	var ctx = $('#'+ selector).get(0).getContext("2d");

	var data = {
		labels: l,

	    //labels: ["January", "February", "March", "April", "May", "June",
		//		"July", "August", "September", "October", "November", "December" ],
	    datasets: [
	        {
	            label: "Download",
	            fillColor: "rgba(220,220,220,0.2)",
	            strokeColor: "rgba(220,220,220,1)",
	            pointColor: "rgba(220,220,220,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(220,220,220,1)",
	            data: d.drx//[65, 59, 80, 81, 56, 55, 40] // d.drx
	        },
	        {
	            label: "Upload",
	            fillColor: "rgba(151,187,205,0.2)",
	            strokeColor: "rgba(151,187,205,1)",
	            pointColor: "rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dtx//[28, 48, 40, 19, 86, 27, 90]
	        },
	        {
	            label: "Total",
	            fillColor: "rgba(151,187,205,0.2)",
	            strokeColor: "#EC7886", //rgba(151,187,205,1)",
	            pointColor: "rgba(151,187,205,1)",
	            pointStrokeColor: "#fff",
	            pointHighlightFill: "#fff",
	            pointHighlightStroke: "rgba(151,187,205,1)",
	            data: d.dt//[28, 48, 40, 19, 86, 27, 90]
	        }
	    ]
	};
	//options = {scaleOverride : true}
	new Chart(ctx).Line(data)//.height(parentheight.width(parentwidth));

}

function getReadableFileSizeString(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);
    return fileSizeInBytes.toFixed(1) + byteUnits[i];
};