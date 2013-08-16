$(function() {

    $('#days').change(function(){
        var selected = $(this).val()
        var list = $.map(selected, function(value) {
            return(value);
        });
        $("#show-days").html(list.join(""));
    });
    
    /* home tabs */
    $('#myTab a').click(function (e) {
      e.preventDefault();
      $(this).tab('show');
    })

});