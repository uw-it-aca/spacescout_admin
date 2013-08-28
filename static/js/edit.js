$(document).ready(function() {

    // fetch spot schema
    (function () {
        $.ajax({
            url: 'api/v1/schema/',
            dataType: 'json',
            success: function (data) {
                var tpl_src,
                    context;

            },
            error: function (xhr, textStatus, errorThrown) {
                var json;

                try {
                    json = $.parseJSON(xhr.responseText);
                    console.log('spot search service error:' + json.error);
                } catch (e) {
                    console.log('Unknown spot service error');
                }
            }
        });
    }());

    var modifiedTime = function (date) {
        var month = date.getMonth() + 1,
            hours = date.getHours(),
            late = (hours > 12),
            pm = late ? 'PM' : 'AM',
            hour = late ? (hours - 12) : hours,
            minutes = (date.getMinutes() < 10) ? '0' + date.getMinutes() : date.getMinutes();

            return month + '/' + date.getDate() + '/' + date.getFullYear()
                + ' ' + hour + ':' + minutes + pm;
    };

});