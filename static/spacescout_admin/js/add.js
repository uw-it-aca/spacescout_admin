$(document).ready(function() {

    // prep for api post/put
    $.ajaxSetup({
        headers: { "X-CSRFToken": window.spacescout_admin.csrf_token }
    });

    var startAddEditor = function (data) {
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

        $('input, textarea, select').change(validate);
        $('input[class*="required-limit-"]').click(limitChoiceCount);
        $('input').keydown(validateInput);
        $('a.btn').click(createSpace);
    };

    var limitChoiceCount = function (e) {
        var m = $(e.target).prop('class').match(/required-limit-(\d+)/);

        if (m && $('input[name="' + $(e.target).prop('name') + '"]:checked').length > m[1]
            && $(e.target).is(':checked')) {
            e.preventDefault();
        }
    };

    var createSpace = function (event) {
        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/space/',
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify(window.spacescout_admin.collectInput()),
            type: "POST",
            success: function (data) {
                var json = $.parseJSON(data);

                window.location.href = window.spacescout_admin.app_url_root + 'space/' + json.id;
            },
            error: XHRError
        });
    };

    var validateInput = function (event) {
        window.spacescout_admin.validateInput(event);
        setInterval(validate, 200);
    };

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
        var m;

        if (v.hasOwnProperty('edit') && v.edit.hasOwnProperty('default')) {
            m = v.edit.default.match(/{{\s*([\S]+)\s*}}/);
            if (m && window.spacescout_admin.hasOwnProperty('vars')
                && window.spacescout_admin.vars.hasOwnProperty(m[1])) {
                return window.spacescout_admin.vars[m[1]];
            }

            return v.edit.default;
        }

        return '';
    };

    // fetch spot data
    $.ajax({
        url: window.spacescout_admin.app_url_root + 'api/v1/schema',
        dataType: 'json',
        success: startAddEditor,
        error: XHRError
    });

});
