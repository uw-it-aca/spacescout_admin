$(document).ready(function() {

    var weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

    // prep for api post/put
    $.ajaxSetup({
        headers: { "X-CSRFToken": window.spacescout_admin.csrf_token }
    });

    // fetch spot data
    (function () {
        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/schema',
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
            url: window.spacescout_admin.app_url_root + 'api/v1/space/' + window.spacescout_admin.space_id,
            dataType: 'json',
            success: function (data) {
                editSpaceDetails(data);
                $('.space-content-loading').hide();
            },
            error: function (xhr, textStatus, errorThrown) {
                XHRError(xhr);
            }
        });
    };

    var editSpaceDetails = function (space) {
        var hash = decodeURIComponent(window.location.hash.substr(1)),
            editor = $('#space-editor'),
            section = null,
            i;

        $('#space-name').html(space.name);

        for (i = 0; i < space.sections.length; i += 1) {
            section = space.sections[i];
            if (hash == section.section) {
                switch(hash) {
                case 'hours' :
                    editHoursDetails(section, editor);
                    break;
                case 'images' :
                    editImageDetails(section, editor);
                    break;
                default:
                    editSectionDetails(section, editor);
                    break;
                }

                validate();

                $('input, textarea').change(validate);
                $('input').keydown(window.spacescout_admin.validateInput);
                $('a.btn').click(modifySpace);

                return;
            }
        }

        editor.append(Handlebars.compile($('#no-section').html())({}));
    };

    var validate = function () {
        window.spacescout_admin.validateFields();
    };

    var modifySpace = function (event) {
        event.preventDefault();

        $.ajax({
            url: window.spacescout_admin.app_url_root + "api/v1/space/" + window.spacescout_admin.space_id + '/',
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify(window.spacescout_admin.collectInput()),
            type: "PUT",
            success: function (data) {
                window.location.href = '/space/' + window.spacescout_admin.space_id;
            },
            error: XHRError
        });
    };

    var editHoursDetails = function (section, editor_node) {
        var section_node = newSectionEditor(section.section),
            anchor_node, hours_node = null, key, days, hours, i, j;

        section_node.append($(Handlebars.compile($('#space-edit-hours').html())({})));

        anchor_node = section_node.find('a').parent();
        if (section.hasOwnProperty('available_hours')
            && typeof section.available_hours === 'object'
            && $.isArray(section.available_hours)) {
            days = section.available_hours;
            hours = {};
            for (i = 0; i < days.length; i += 1) {
                if (days[i].hasOwnProperty('hours')) {
                    for (j = 0; j < days[i].hours.length; j++) {
                        if (days[i].hours[j].length == 2) {
                            key = days[i].hours[j][0] + '-' + days[i].hours[j][1];
                            if (hours.hasOwnProperty(key)) {
                                hours[key].days.push(days[i].day);
                            } else {
                                hours[key] = {
                                    days: [ days[i].day ],
                                    hours: days[i].hours[j]
                                };
                            }
                        }
                    }
                }
            }

            for (i in hours) {
                hours_node = hoursNode(hours[i]);
                anchor_node.before(hours_node);
            }
        }

        if (!hours_node) {
            anchor_node.before(hoursNode());
        }

        appendSectionFields(section.fields, section_node);

        editor_node.append(section_node);

        $('#space-editor #add-hours').click(function (e) {
            hoursNode().insertBefore($(e.target).parent());
        });
    };

    var hoursNode = function (t) {
        var tpl = Handlebars.compile($('#hours-editor').html()),
            edit_node = $(tpl()),
            select_days = edit_node.find('select#days'),
            select_open = edit_node.find('select#opening-time'),
            select_close = edit_node.find('select#closing-time'),
            i, option;

        for (i = 0; i < weekdays.length; i += 1) {
            option = $('<option></option>').val(weekdays[i]).html(gettext(weekdays[i])).addClass('hours-value');
            if (t && t.hasOwnProperty('days') && $.inArray(weekdays[i], t.days) > -1) {
                option.attr('selected', 'selected');
            }

            select_days.append(option);
        }

        appendHours(select_open, (t) ? t.hours[0] : null);
        appendHours(select_close, (t) ? t.hours[1] : null);

        select_open.change(function () {
            var node = select_close.find('option[value="' + $(this).val() + '"]');
            select_close.find('option').removeAttr('disabled');
            node.attr('disabled','disabled');
            node.prevAll('option').attr('disabled','disabled');
        });

        select_close.change(function () {
            var node = select_open.find('option[value="' + $(this).val() + '"]');
            select_open.find('option').removeAttr('disabled');
            node.attr('disabled','disabled');
            node.nextAll('option').attr('disabled','disabled');
        });

        if (window.spacescout_admin.is_mobile) {
            // MOBILE: handle multi-day selection and display
            select_days.addClass('form-control day-select');
            select_days.change(function(){
                var selected = $(this).val(),
                    list;

                if (selected) {
                    list = $.map(selected, function(value) {
                        return(gettext(value));
                    });
            
                    $(this).siblings(".show-days").html(list.join(", "));
                }
            });
            
            select_days.trigger('change');
            
        } else {
            // DESKTOP: make the multi-day selector usable
            select_days.selectpicker();
        }

        return edit_node;
    };

    var appendHours = function (select, choice) {
        var i;

        for (i = 0; i < 24; i += 1) {
            appendHoursOption(select, i, 0, choice);
            appendHoursOption(select, i, 30, choice);
        }

        appendHoursOption(select, 23, 59, choice);
    };

    var appendHoursOption = function (select, hour, minute, choice) {
        var am = gettext('am'),
            pm = gettext('pm'),
            value = leadingZero(hour) + ':' + leadingZero(minute),
            option = $('<option></option>').val(value).addClass('hours-value');

        if (choice == value) {
            option.attr('selected', 'selected');
        }

        if (hour == 0 && minute == 0) {
            option.html(gettext('midnight'));
        } else if (hour == 12 && minute == 0) {
            option.html(gettext('noon'));
        } else {
            option.html(String((hour < 13) ? hour : (hour - 12))
                        + ':' + leadingZero(minute)
                        + ((hour > 11) ? pm : am));
        }

        return select.append(option);
    };

    var leadingZero = function (n) {
        return (n < 10) ? '0' + n : String(n);
    };

    var editImageDetails = function (section, editor_node) {
        var section_node = newSectionEditor(section.section),
            tpl = Handlebars.compile($('#space-edit-images').html()),
            context = {};

        context['images'] = section['images'];
        if (context['images'].length) {
            if (context['images'].length > 0) {
                context['images'][0]['active'] = 'active';
            }
        }

        section_node.append($(tpl(context)));

        editor_node.append(section_node);

        $('#upload_form').ajaxForm({
            type: 'POST',
            url : window.spacescout_admin.app_url_root + 'api/v1/space/' + window.spacescout_admin.space_id + '/image/',
            dataType: 'json',
            beforeSubmit: function (formData) {
                var i;

                for (i = 0; i < formData.length; i += 1) {
                    if (formData[i].name == 'image' && !formData[i].value) {
                        return false;
                    }
                }

                return true;
            },
            success: function (responseJSON) {
                console.log('response is ' + responseJSON.id);
            },
            error: function () {
                console.log('ERROR');
            }
        });

        $('#delete_button').click(function (e) {
            var img_src = $('#image-carousel .active img').prop('src'),
                id = img_src.match(/\/(\d+)$/)[1];

            $.ajax({
                url: img_src,
                type: "DELETE",
                success: function (data) {
                    console.log('Image ' + id + ' Deleted.');
                },
                error: function () {
                    console.log('ERROR');
                }
            });
        });
    };

    var editSectionDetails = function (section, editor_node) {
        var section_node = newSectionEditor(section.section);

        appendSectionFields(section.fields, section_node);
        editor_node.append(section_node);
    };

    var newSectionEditor = function (title) {
        return $(Handlebars.compile($('#editor-container').html())({
            section: gettext(title)
        }));
    };

    var appendSectionFields = function (fields, section) {
        var i;

        for (i = 0; i < fields.length; i += 1) {
            if (typeof fields[i].value === 'object') {
                if ($.isArray(fields[i].value)) {
                    window.spacescout_admin.appendFieldList(fields[i], getFieldValue, section);
                } else {
                    window.spacescout_admin.appendFieldValue(fields[i], getFieldValue, section);
                }
            }
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
        return window.spacescout_admin.getFieldValue(v);
    };
});