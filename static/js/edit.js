$(document).ready(function() {


    // fetch spot data
    (function () {
        $.ajax({
            url: '/api/v1/schema',
            dataType: 'json',
            success: function (data) {
                window.spacescout_admin.spot_schema = data;
                loadSpaceDetails();
            },
            error: function (xhr, textStatus, errorThrown) {
                XHRError(xhr);
            }
        });
    }());

    var loadSpaceDetails = function () {
        $.ajax({
            url: '/api/v1/space/' + window.spacescout_admin.spot_id,
            dataType: 'json',
            success: function (data) {
                window.spacescout_admin.spot_data = data;
                editSpaceDetails();
            },
            error: function (xhr, textStatus, errorThrown) {
                XHRError(xhr);
            }
        });
    };

    var editSpaceDetails = function () {
        var spot = window.spacescout_admin.spot_data,
            hash = decodeURIComponent(window.location.hash.substr(1));

        $('#space-name').html(spot.name);

        switch(hash) {
        case 'basic' :
            $('#space_editor').html(editBasicInfo(spot));
            break;
        case 'hours' :
            $('#space_editor').html(editHoursInfo(spot));

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
            
            break;
        case 'images' :
            $('#space_editor').html(editImageInfo(spot));
            break;
        case 'location' :
            $('#space_editor').html(editLocationInfo(spot));
            break;
        case 'access' :
            $('#space_editor').html(editAccessInfo(spot));
            break;
        case 'resources & environment':
            $('#space_editor').html(editResourcesInfo(spot));
            break;
        default:
            $('#space_editor').html(Handlebars.compile($('#no-section').html())({}));
            break;
        }
    };

    var editBasicInfo = function () {
        var spot = window.spacescout_admin.spot_data,
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-basic').html()),
            context = {
                name: spot.name,
                manager: spot.manager,
                types: [],
                editors: spot.editors.join(', ')
            },
            i, j, checked;

        for (i = 0; i < schema.type.length; i += 1) {
            checked = '';

            for (j = 0; j < spot.type.length; j += 1) {
                if (spot.type[j] == schema.type[i]) {
                    checked = 'checked';
                    break;
                }
            }

            context.types.push({
                name: gettext(schema.type[i]),
                value: 'schema.type[i]',
                checked: checked
            });
        }

        return tpl(context);
    };

    var editHoursInfo = function (spot) {
        var spot = window.spacescout_admin.spot_data,
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-hours').html());

        return tpl({});
    };

    var editImageInfo = function (spot) {
        var spot = window.spacescout_admin.spot_data,
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-images').html());

        return tpl({});
    };

    var editLocationInfo = function (spot) {
        var spot = window.spacescout_admin.spot_data,
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-location').html());

        return tpl({});
    };

    var editAccessInfo = function (spot) {
        var spot = window.spacescout_admin.spot_data,
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-access').html());

        return tpl({});
    };

    var editResourcesInfo = function (spot) {
        var spot = window.spacescout_admin.spot_data,
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-resources').html());

        return tpl({});
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

});