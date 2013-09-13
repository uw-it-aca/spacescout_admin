$(document).ready(function() {

    // fetch spot data
    (function () {
        $.ajax({
            url: '/api/v1/schema',
            dataType: 'json',
            success: function (data) {
                var editor = $('.space-add-section > div'),
                    fields = window.spacescout_admin.fields,
                    i;

                window.spacescout_admin.spot_schema = data;

                for (i = 0; i < fields.length; i += 1) {
                    if (typeof fields[i].value === 'object') {
                        if ($.isArray(fields[i].value)) {
                            window.spacescout_admin.appendFieldList(fields[i], getFieldValue, editor);
                        } else {
                            window.spacescout_admin.appendFieldValue(fields[i], getFieldValue, editor);
                        }
                    }
                }

                validate();
                $('input, textarea').change(validate);
            },
            error: function (xhr, textStatus, errorThrown) {
                XHRError(xhr);
            }
        });
    }());

    var validate = function () {
        window.spacescout_admin.validateFields();
        if ($('.required-field-icon:visible').length == 0) {
            $('a.btn').removeAttr('disabled');
        } else {
            $('a.btn').attr('disabled', 'disabled');
        }
    };

    var XHRError = function (xhr) {
        var json;

        try {
            json = $.parseJSON(xhr.responseText);
            console.log('space query service error:' + json.error);
        } catch (e) {
            console.log('Unknown space service error: ' + xhr.responseText);
        }
    };

    var getFieldValue = function (v) {
        return '';
    };
});