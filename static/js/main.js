(function(w){


	$(document).ready(function() {
		getSpaceCount();

		toggleEditExportButtons();
	});

	$(w).resize(function(){ //Update dimensions on resize

	});


	// check individual checkboxes
	$('#space_list_body tr input:checkbox').click(function(){

        // check the corresponding checkbox
        $(this).prop('checked', this.checked);
        // toggle buttons based on checkbox
        toggleEditExportButtons();

     });


	// check all checkboxes
	$('#check_all_checkbox').click(function(){

    	// check all the checkboxes
    	$(this).closest('table').find(':checkbox').prop('checked', this.checked);
    	// toggle buttons based on checkboxes
    	toggleEditExportButtons();
	});

	// export button
	$('#export_button').click(function(e) {

        if($('#export_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {
            window.location.href = '/download';
            return false;
        }

    });

	// edit button
	$('#edit_button').click(function(e) {

        if($('#edit_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {
            window.location.href = '/edit';
            return false;
        }

    });

    // save button
	$('#save_button').click(function() {
        window.location.href = '/';
        return false;
    });

    // cancel button
	$('#cancel_button').click(function() {
        window.location.href = '/';
        return false;
    });

	// get a count of spaces
	function getSpaceCount() {
    	var rowCount = $('#space_list_body tr').length;
    	console.log(rowCount);
	}

	// toggle edit and export buttons
	function toggleEditExportButtons() {

    	if($('#space_list_body tr input:checkbox:checked').length > 0){
        	$('#edit_button').removeClass('disabled');
        	$('#export_button').removeClass('disabled');
    	}
    	else {
        	$('#edit_button').addClass('disabled');
        	$('#export_button').addClass('disabled');
    	}
	}



})(this);