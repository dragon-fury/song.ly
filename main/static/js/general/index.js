(function() {

	$('form').on('submit', function(e) {

		var input = $(this).parents('.userid').find(':text');

		$.ajax({
			method: "POST",
			url: "/",
			data: {
				"user_id": input.val()
			}
		}).done(function(data) {
			
		});
	});
})();