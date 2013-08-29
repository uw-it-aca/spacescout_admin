$(document).ready(function() {
    
    // mocking up the multi-day-select for hours editing
    $('#days').change(function(){
        var selected = $(this).val();

        var list = $.map(selected, function(value) {
            return(value);
        });
        $("#show-days").html(list.join(""));
    });
    
});