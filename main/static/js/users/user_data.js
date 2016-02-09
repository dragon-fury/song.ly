(function() {

	var userid = parseInt(window.location.pathname.split("/")[2]);

	$.ajax({
		method: "GET",
		url: "/recommended_friends/"+userid
	}).done(function(data) {
		var s = "";
		s += '<div class="row">';
		s += '<div class="col-md-12">';
		for(var i=0; i < data.friends.length; i++) {
			s += '<div class="row friend_box">';
			s += '<div class="col-md-4"><img src="/static/images/friend_icon.png" /></div>';
			s += "<div class='col-md-8'><p style='text-align:center'><span>"+data.friends[i].name+"</span></p>";
			s += "<p style='text-align:center'><span>"+data.friends[i].location+"</span></p></div>";
			s += "</div>";
		}
		if(data.friends.length === 0) {
			s += '<div>No suggestions to show</div>';
		}
		s += "</div></div>";
		$(".songs_friend").append(s);
	});

	$.ajax({
		method: "GET",
		url: "/recommended_songs/"+userid
	}).done(function(data) {
		var s = "";
		var year = "NA";
		for(var i=0;i < data.songs.length && i<6; i++) {
			if(data.songs[i].year !== '0') {
				year = data.songs[i].year;
			}
			s += '<div class="col-xs-4 col-md-2">';
			s += '<div class="thumbnail"><img src="/static/images/icon.png" /></div>'
			s += "<div class='caption'><p style='text-align:center'><span>"+data.songs[i].title+"</span></p>";
			s += "<p style='text-align:center'><span>"+year+"</span></p></div>";
			s += "</div>";
		}
		if(s === "") {
			s = '<div>No suggestions to show</div>';
		}
		$(".songs_amazon").append(s);
	});

	$.ajax({
		method: "GET",
		url: "/artists/Palo Alto"
	}).done(function(data) {
		var s = "";
		for(var i=0;i < data.detail.length && i<6; i++) {
			s += '<div class="col-xs-4 col-md-2">';
			s += '<div class="thumbnail"><img src="/static/images/map_pin.png" /></div>'
			s += "<div class='caption'><p style='text-align:center; text-transform:capitalize;'><span>"+data.detail[i]+"</span></p></div>";
			s += "</div>";
		}
		if(s === "") {
			s = '<div>No suggestions to show</div>';
		}
		$(".local_artists").append(s);
	});

	$.ajax({
		method: "GET",
		url: "/users/"+userid+"/recentsongs"
	}).done(function(data) {
		var s = "";
		s += '<div class="row">';
		s += '<div class="col-md-12">';

		for(var i=0; i < data.songs.length; i++) {
			s += '<div class="row friend_box">';
			s += '<div class="col-md-4"><img src="/static/images/icon.png" /></div>';
			s += "<div class='col-md-8'><p><span class='title'>"+data.songs[i].title+"</span></p></div>";
			s += "<p><span>"+data.songs[i].artist_name+"</span></p>";
			s += "</div>";
		}

		if(data.songs.length === 0) {
			s = '<div>No recent list</div>';
		}

		s += "</div></div>";
		$(".recently").append(s);
	});

	(function poll() {
		$.ajax({
			method: "GET",
			url: "/songs/trending",
			dataType: "json",
			// complete: poll,
			timeout: 10000
		}).done(function(data) {
			var s = "";
			s += '<div class="row">';
			s += '<div class="col-md-12">';
			data.trending.sort(function(a,b){ return b.count - a.count;})
			for(var i=0; i < data.trending.length; i++) {
				s += '<div class="row friend_box">';
				s += '<div class="col-md-4"><img src="/static/images/icon.png" /></div>';
				s += "<div class='col-md-8'><p><span class='title'>"+data.trending[i].title+"</span></p>";
				s += "<p><span>"+data.trending[i].artist+"</span></p>";
				s += "<p><span>"+data.trending[i].count+"</span></p></div>";
				s += "</div>";
			}
			s += "</div></div>";
			$(".songs_trending").html(s);
		});
	})();
})();