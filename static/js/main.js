$(document).ready(function() {
    
    // handle multi-day selection and display
    $('.day-select').change(function(){
        var selected = $(this).val();

        var list = $.map(selected, function(value) {
            return(value);
        });
        
        $(this).siblings(".show-days").html(list.join(""));
    });
    
});