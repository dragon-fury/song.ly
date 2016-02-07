(function() {

	var userid = parseInt(window.location.pathname.split("/")[2]);

	var listen = function(evt) {
		var user_name = $("#focusedInput").val();

		$.ajax({
			url: "/users/"+user_name,
			method: "GET"
		}).done(function(data) {
			if(!$.isEmptydata !== )
		});

	};

	$.ajax({
		method: "GET",
		url: "/recommended_friends/"+userid
	}).done(function(data) {
		var s = "";
		for(var i=0;i<6; i++) {
			s += '<div class="col-xs-4 col-md-2">';
			s += '<div class="thumbnail"><img src="/static/images/friend_icon.png" /></div>'
			s += "<div class='caption'><p style='text-align:center'><span>"+data.friends[i].name.split("_")[0]+"</span></p></div>";
			s += "</div>";
		}
		$(".songs_friend").html(s);
	});

	$.ajax({
		method: "GET",
		url: "/recommended_songs/"+userid
	}).done(function(data) {
		var s = "";
		var year = "NA";
		for(var i=0;i<6; i++) {
			if(data.songs[i].year !== '0') {
				year = data.songs[i].year;
			}
			s += '<div class="col-xs-4 col-md-2">';
			s += '<div class="thumbnail"><img src="/static/images/icon.png" /></div>'
			s += "<div class='caption'><p style='text-align:center'><span>"+data.songs[i].title+"</span></p>";
			s += "<p style='text-align:center'><span>"+year+"</span></p></div>";
			s += "</div>";
		}
		$(".songs_amazon").html(s);
	});

	$.ajax({
		method: "GET",
		url: "/artists/Palo Alto"
	}).done(function(data) {
		var s = "";
		for(var i=0;i<6; i++) {
			s += '<div class="col-xs-4 col-md-2">';
			s += '<div class="thumbnail"><img src="/static/images/map_pin.png" /></div>'
			s += "<div class='caption'><p style='text-align:center; text-transform:capitalize;'><span>"+data.detail[i]+"</span></p></div>";
			s += "</div>";
		}
		$(".local_artists").html(s);
	});
})();