(function(){
	var currentQnum = 0,
		prevQnum = currentQnum;

	var replaceSpace = function(str) {
		return str.replace(/\s/g, "");
	};

	var updateVisuals = function(qnum) {
		clusterConcepts.clearHandle();

		$.ajax({
		    url: "concepts?qnum="+qnum,
		    type: "GET",
		    processData: false,
		    contentType: 'application/json'
		}).done(function(data) {
			var conceptsForQestion = data.data;
			clusterConcepts.createPack(conceptsForQestion);
		});
	};

	var hideAndSeek = function(qnum) {
		$("div.q"+prevQnum).addClass("hidden");
		$("div.q"+(qnum)).removeClass("hidden");
		$("div.a"+prevQnum).addClass("hidden");
		$("div.a"+(qnum)).removeClass("hidden");
		$("input.s"+prevQnum).addClass("hidden");
		$("input.s"+(qnum)).removeClass("hidden");
		prevQnum = qnum;
	};

	var saveChanges = function(e) {
		var qnum = $(".pagination li.active a").attr("class");
		var questionContainer = $(".qacontent.q"+qnum);
		var answerContainer = $(".answers.a"+qnum);
		var scoreContainer = $(".score.s"+qnum);
		
		var data = {
			"question": questionContainer.text().trim().replace(/\s+\n/g, ",- "),
			"answer": answerContainer.text().trim(),
			"score": $("input.s"+qnum).val(),
			"concepts": clusterConcepts.getUpdateList(),
			"excludeConcepts": clusterConcepts.getExclusionList(),
			"qnum": qnum
		};

		$.ajax({
		    url: "author_mode/update_changes",
		    type: "POST",
		    processData: false,
		    contentType: 'application/json',
		    data: JSON.stringify(data)
		}).done(function(data) {
			updateVisuals(qnum);
		});
	};


	$(".save-changes").on("click", saveChanges);

	$(".pagination li a").on("click", function(e){
		$(".pagination li").removeClass("active");
		$(this).parent().addClass("active");
		var qnum = parseInt($(this).attr("class"));
		hideAndSeek(qnum);
		updateVisuals(qnum);
	});

	$(".paper").on("click", function(e) {
		$.ajax({
		    type: "POST",
		    url: "/download_paper"
		});
	});

	var data = {};
	var params = location.pathname.split("/");
	data["term"] = params[1];
	data["year"] = Number(params[2]);
	data["classname"] = params[3];
	data["test"] = params[4];

    $(".mapping").attr("href", "/download_concept_mapping?"+$.param(data));
    $(".paper").attr("href", "/download_paper?"+$.param(data));

	updateVisuals(currentQnum);

})();