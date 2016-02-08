(function() {

	$('form').on('submit', function(e) {
		e.preventDefault();
		e.stopPropagation();

		var user_name = $("#focusedInput").val();

		$.ajax({
			method: "GET",
			url: "/user_name/"+user_name

		}).done(function(data){
			window.location = "/users/"+data
		});
	});
})();