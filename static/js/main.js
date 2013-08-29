$(document).ready(function() {
    
    // make the multi-day selector usable for desktop
    $('.selectpicker').selectpicker();
    
    // handle multi-day selection and display
    $('.day-select').change(function(){
        var selected = $(this).val();

        var list = $.map(selected, function(value) {
            return(value);
        });
        
        $(this).siblings(".show-days").html(list.join(""));
    });
    
});