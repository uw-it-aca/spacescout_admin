(function($) {

var $event = $.event,
	$special,
	resizeTimeout;

$special = $event.special.debouncedresize = {
	setup: function() {
		$( this ).on( "resize", $special.handler );
	},
	teardown: function() {
		$( this ).off( "resize", $special.handler );
	},
	handler: function( event, execAsap ) {
		// Save the context
		var context = this,
			args = arguments,
			dispatch = function() {
				// set correct event type
				event.type = "debouncedresize";
				$event.dispatch.apply( context, args );
			};

		if ( resizeTimeout ) {
			clearTimeout( resizeTimeout );
		}

		execAsap ?
			dispatch() :
			resizeTimeout = setTimeout( dispatch, $special.threshold );
	},
	threshold: 150
};

})(jQuery);

(function(w){

    var winH = $(window).height();
    var winW = $(window).width();
    var headerH = $(".navbar").height();
    var alertH = $(".alert").height();
    var filterH = $("#filter_block").height();
    var tableContainerH = winH - headerH - alertH - filterH - 90;  // approximation height of table container

    var tableContainerW = $("#table_scroller_container").width();

	$(document).ready(function() {

    	// show the success message
		var success = GetQueryStringParams('q');
		if (success) {
    		$('#success_message').show();
		}
		else {
    		$('#success_message').hide();
		}

		getSpaceCount();
		toggleEditExportButtons();

		$('.dropdown-toggle').dropdown();

		$(".populate-column").tooltip({
            'placement': 'top',
            'animation': true,
        });

        buildScrollTable();

        // handle scrolling
        $(".fixedContainer > .fixedTable", ".fixedArea").scroll(function() {
            handleScroll();
        });


	});

    $(w).on("debouncedresize", function( event ) {

        console.log("resize");

        buildScrollTable();

    });


    /*$(w).resize(function() {
        console.log("resize");

        // reset base widths
        winH = $(window).height();
        winW = $(window).width();
        headerH = $(".navbar").height();
        alertH = $(".alert").height();
        filterH = $("#filter_block").height();
        tableContainerH = winH - headerH - alertH - filterH - 90;  // approximation height of table container
        tableContainerW = $("#table_scroller_container").width();

        // set widths for table container
        $(".fixedArea").width(tableContainerW);
        $(".fixedContainer").width(tableContainerW - 302);
        $(".fixedContainer .fixedHead").width(tableContainerW - 302);
        $("#table_scroller").width(tableContainerW - 302);
    });*/


	//show filter block
	$('#filter_block_button').click(function(e){
    	e.preventDefault();
    	$('#filter_block').toggleClass('slidedown');
        // wait for the filter block to slide down before resetting the table scroll height
        setTimeout(buildScrollTable, 699);
	});


	// check individual checkboxes
	$('.fixedTable tr input:checkbox').live("click", function(e){

        // check the corresponding checkbox
        $(this).attr('checked', true);
        // toggle buttons based on checkbox
        toggleEditExportButtons();
     });

	// check all checkboxes
	$('#check_all_checkbox').live("click", function(e){

    	// check all the checkboxes
        if($("#check_all_checkbox").is(':checked')){
            $('.fixedTable').find(':checkbox').attr('checked', true);
        } else {
            $('.fixedTable').find(':checkbox').attr('checked', false);
        };

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
            var space_count = $('.fixedTable tr input:checkbox:checked').length;
            // pass number of checked spaces to hidden field
            $('#checked_spaces_count').val(space_count);
        }

    });

    // save button
	$('#save_button').click(function(e) {

    	$(".table-container input:text:visible").each(function (i) {
        	if ( $(this).val().length === 0 ) {
            	$(this).addClass("blah");
        	}
        	else {
            	$(this).removeClass("blah");
        	}
    	});

    	var empties = $('.blah').length;

    	if (empties == 0){
        	window.location.href = '/?q=success';
    	}
    	else {
        	$('#error_message').show();
    	}

    	console.log(empties);

    	// if any visible input are empty, show error alert
    	/*if( $('.table-container').find('input:text:visible').val().length == 0 ) {
        	$('#error_message').show();
    	}
    	else {
        	// else go back to space list page
        	window.location.href = '/?q=success';
    	}*/


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

    // add space button
    $('#add_space_button').click(function(e) {

    	// disable the add spaces button by default unless a space has been "checked"
        if($('#add_space_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {

        }

    });

    // add multiple spaces button
    $('#add_multiple_button').click(function(e) {

    	// disable the add spaces button by default unless a space has been "checked"
        if($('#add_multiple_button').hasClass('disabled')) {
            e.preventDefault();
        }
        else {

        }

    });

    // add rows button
    $('#add_rows_button').click(function(e) {
        e.preventDefault();
        $('.add-new').show();
        setTableScrollHeight();
    });

	// get a count of spaces
	function getSpaceCount() {
    	var rowCount = $('#space_list_body tr').length;
    	$('#table_num_spaces').html(rowCount + "&nbsp;spaces");
	}

	// toggle edit and export buttons
	function toggleEditExportButtons() {

    	if($('.fixedTable .col-checkbox input:checkbox:checked').length > 1){

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

	function buildScrollTable() {

    	// reset base widths
        winH = $(window).height();
        winW = $(window).width();
        headerH = $(".navbar").height();
        alertH = $(".alert").height();
        filterH = $("#filter_block").height();
        tableContainerH = winH - headerH - alertH - filterH - 90;  // approximation height of table container
        tableContainerW = $("#table_scroller_container").width();

    	// set widths for table container
        $(".fixedArea").width(tableContainerW);
        $(".fixedContainer").width(tableContainerW - 302);
        $(".fixedContainer .fixedHead").width(tableContainerW - 302);
        $("#table_scroller").width(tableContainerW - 302);

        /*$("#table_scroller").height(tableContainerH - 30);
        $(".fixedTable").height(tableContainerH - 30);
        $(".fixedColumn").height(tableContainerH + 1);*/

        $("#table_scroller").css("max-height", tableContainerH - 30);
        $(".fixedTable").css("max-height", tableContainerH - 30);
        $(".fixedColumn").css("max-height", tableContainerH + 1);

        console.log("dsalkfj");
	}

	function GetQueryStringParams(sParam) {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++)
        {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == sParam)
            {
                return sParameterName[1];
            }
        }
    }

    // Handle the scroll events
    function handleScroll() {
        //Find the scrolling offsets
        var tblarea = $('#table_scroller');
        var x = tblarea[0].scrollLeft;
        var y = tblarea[0].scrollTop;

        $(".fixedColumn .fixedTable")[0].scrollTop = y;
        //$(mainid + " ." + classColumn + " > .fixedTable")[0].scrollTop = y;

        $(".fixedContainer .fixedHead")[0].scrollLeft = x;
        //$(mainid + " .fixedContainer > ." + classHeader)[0].scrollLeft = x;

    }

})(this);