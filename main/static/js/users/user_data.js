(function() {

	var userid = parseInt(window.location.pathname.split("/")[2]);

	$.ajax({
		method: "GET",
		url: "/recommended_friends/"+userid
	}).done(function(data) {
		var s = "";
		for(var i=0; i < data.friends.length && i<6; i++) {
			s += '<div class="col-xs-4 col-md-2">';
			s += '<div class="thumbnail"><img src="/static/images/friend_icon.png" /></div>'
			s += "<div class='caption'><p style='text-align:center'><span>"+data.friends[i].name+"</span></p></div>";
			s += "</div>";
		}
		if(s === "") {
			s = '<div>No suggestions to show</div>';
		}
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
})();