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
    var filterH = $("#filter_block").height();
    var tableContainerH = winH - headerH - filterH - 90;  // approximation height of table container

    var tableContainerW = $("#table_scroller_container").width();

	$(document).ready(function() {

        $('#id_username').focus()

		getSpaceCount();
		toggleEditExportButtons();

		$('.dropdown-toggle').dropdown();

		$(".populate-column").tooltip({
            'placement': 'top',
            'animation': true,
        });
        
        buildScrollTable();

        // handle scrolling - default browser
        $(".fixedContainer > .fixedTable", ".fixedArea").scroll(function() {
            handleScroll();
        });

	});

    $(w).on("debouncedresize", function( event ) {
        buildScrollTable();
    });

	//show filter block
	$('#filter_block_button').click(function(e){

    	//console.log("sadlkjfalsdfkja");
    	e.preventDefault();
    	$('#filter_block').toggleClass('slidedown');
        // wait for the filter block to slide down before resetting the table scroll height
        setTimeout(buildScrollTable, 699);
	});


	// check individual checkboxes
	$('.fixedTable tr input:checkbox').live("click", function(e){

        // check the corresponding checkbox
        if($(this).is(':checked')){
            $(this).attr('checked', true);
        }
        else {
            $(this).attr('checked', false);
        }

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

    // switch campuses dropdown menu
    $('#campus_switcher a').click(function(e) {

        e.preventDefault();

        // if what was clicked is already active - don't do anything
        // otherwise do the switch - change the menu to reflect selected item and re-run the webservice query

        if ($(this).hasClass('selected')) {
            return false
        }
        else {
             // replace this alert with actual fuction to display campus spaces
             alert("switch campus!");

             //remove previously selected item
             if ($('#campus_switcher a').hasClass('selected')) {
                 $('#campus_switcher a').removeClass();
             }

             //add the selected class
             $(this).addClass('selected');

             // change the name in the dropdown menu
             $('#campus_name_dropdown span').html($(this).html());
        }


    });

    // hover table rows
    $("#table_scroller_container table tbody").delegate('td','mouseover mouseleave', function(e) {

        // get the id and strip out any characters
        var id = $(this).parent().attr("id").toString();
        id = id.replace(/\D/g,'');

        // add hover class to the matching spot id's row
        if (e.type == 'mouseover') {
          $("#spot_" + id + "_fixed").addClass("hover");
          $("#spot_" + id + "_scroll").addClass("hover");
        }
        else {
          $("#spot_" + id + "_fixed").removeClass("hover");
          $("#spot_" + id + "_scroll").removeClass("hover");
        }
    });

    // handle popover clicks
    $('[rel="popover"]').popover({
        title: 'Bulk Edit',
        html: true,
        placement: 'bottom',
        content: function(){
            return setPopoverContent($(this).siblings().html());
        }
    }).click(function(e) {
        e.preventDefault();

        $(this).siblings().find("#bulk_edit_input").focus(); // find child siblings that is the bulk input and put focus
        $('.bulk-edit').not(this).popover('hide'); //hide any popovers currently open
    });

    // create popover content
    function setPopoverContent(columnName) {
        
        $('#settings-layout-content .column-name').html(columnName);
        return $('#settings-layout-content').html();
    }

    // handle closing the popover
    $('#bulk_edit_close').live("click", function(e){
        e.preventDefault();
        //hide any open popover
        $('[rel="popover"]').popover('hide');
    });

    // handle the button to change all column values
    $('#bulk_edit_submit').live("click", function(e){
        e.preventDefault();

        //populate column values - need to set this dynamically
        var columnClass = $(this).closest('td').children().attr('class');
        populateColumnValues(columnClass);

    });

    // handle when user hits "enter" button instead of clicking button
    $('#bulk_edit_input').live('keypress', function (e) {
        if(e.keyCode == 13){
            $('#bulk_edit_submit').trigger('click');
        }
    });


    // handle the single spot search
    $('#search_single_spot_input').keypress(function(e) {
        if(e.keyCode == 13){
            $('#search_single_spot_button').trigger('click');
        }
    });

    $('#search_single_spot_button').click(function(e) {
        e.preventDefault();
        var space_id = $('ul.typeahead li.active').data('value').match(/\d+/);
        window.location.href = "/space/" + space_id;
    });

    function populateColumnValues(columnClass) {

        var newValue = $('#bulk_edit_input').val();

        // specify the column and the value to be inserted
        $('tbody .' + columnClass + ' input').val(newValue);
        $('tbody .' + columnClass + ' input').css('color', 'red');

        // close the popover and do some color changing to signify the changes
        $('[rel="popover"]').popover('hide');
        setTimeout(function(){ $('tbody .' + columnClass + ' input').delay('2000').removeAttr('style')}, 2500);
    }

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
        filterH = $("#filter_block").height();
        fixedW = $(".fixedColumn").width() + 2;
        tableOptionsH = $(".table-options").height();

        tableContainerH = winH - headerH - filterH - 90;  // approximation height of table container
        tableContainerW = $("#table_scroller_container").width();

    	// set widths for table container
        $(".fixedArea").width(tableContainerW);

        $(".fixedContainer").width(tableContainerW - fixedW);
        $(".fixedContainer .fixedHead").width(tableContainerW - fixedW);
        $("#table_scroller").width(tableContainerW - fixedW);

        $("#edit_space_scroller").css("max-height", tableContainerH - tableOptionsH - 20);

        $("#table_scroller").css("max-height", tableContainerH - 55);
        $(".fixedTable").css("max-height", tableContainerH - 55);
        $(".fixedColumn").css("max-height", tableContainerH + 1);
        $("#upload_page_container").css("max-height", tableContainerH / 1.25);
        $("#upload_page_container").css("overflow", "auto");

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
        //var tblarea = $('.lb-wrap');

        var x = tblarea[0].scrollLeft;
        var y = tblarea[0].scrollTop;

        $(".fixedColumn .fixedTable")[0].scrollTop = y;
        //$(mainid + " ." + classColumn + " > .fixedTable")[0].scrollTop = y;

        $(".fixedContainer .fixedHead")[0].scrollLeft = x;
        //$(mainid + " .fixedContainer > ." + classHeader)[0].scrollLeft = x;

        //hide any open popover
        $('[rel="popover"]').popover('hide');

    }

})(this);
