(function(w){


	$(document).ready(function() {
		setTableScrollHeight();
		getSpaceCount();
		toggleEditExportButtons();
	});

	$(w).resize(function(){ //Update dimensions on resize
    	setTableScrollHeight();
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

    	// disable the edit button by default unless a space has been "checked"
        if($('#edit_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {
            var space_count = $('#space_list_body tr input:checkbox:checked').length;
            // pass number of checked spaces to hidden field
            $('#checked_spaces_count').val(space_count);
        }

    });

    // save button
	$('#save_button').click(function() {


    });

    // cancel button
	$('#cancel_button').click(function() {
        window.location.href = '/';
        return false;
    });

    // batch upload button
    $('#batch_upload_button').click(function(e) {

    	// disable the batch upload button by default unless a space has been "checked"
        if($('#batch_upload_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {

        }

    });

    // add spaces button
    $('#add_spaces_button').click(function(e) {

    	// disable the add spaces button by default unless a space has been "checked"
        if($('#add_spaces_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {

        }

    });

    // add rows button
    $('#add_rows_button').click(function(e) {
        e.preventDefault();
        $('.add-new').show();
    });

	// get a count of spaces
	function getSpaceCount() {
    	var rowCount = $('#space_list_body tr').length;
    	$('#table_num_spaces').html(rowCount + "&nbsp;spaces");
	}

	// toggle edit and export buttons
	function toggleEditExportButtons() {

    	if($('#space_list_body tr input:checkbox:checked').length > 0){

        	$('#edit_button').removeClass('disabled');
        	$('#export_button').removeClass('disabled');

        	$('#batch_upload_button').addClass('disabled');
        	$('#add_multiple_button').addClass('disabled');
        	$('#add_space_button').addClass('disabled');
    	}
    	else {

        	$('#edit_button').addClass('disabled');
        	$('#export_button').addClass('disabled');

        	$('#batch_upload_button').removeClass('disabled');
        	$('#add_multiple_button').removeClass('disabled');
        	$('#add_space_button').removeClass('disabled');
    	}
	}

	function setTableScrollHeight() {
    	var winH = $(window).height();
        var headerH = $("#header").height();
        $("#table_scroller_container").height(winH - headerH - 120); // approximation height
	}



})(this);