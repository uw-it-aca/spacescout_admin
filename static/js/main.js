(function(w){


	$(document).ready(function() {
		doSomething();

	});

	$(w).resize(function(){ //Update dimensions on resize
		doSomething();
	});

	//Check if Mobile
	function doSomething() {

	}


	// check all checkboxes
	$('#check_all').click(function(){
    	$('.check').find(':checkbox').attr('checked', this.checked);
	});



})(this);