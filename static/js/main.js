$(document).ready(function() {

    $('#days').change(function(){
        var selected = $(this).val();

        var list = $.map(selected, function(value) {
            return(value);
        });
        $("#show-days").html(list.join(""));
    });
    
});