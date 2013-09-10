$(document).ready(function() {

    var weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        
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

        if (hash == 'basic') {
            editBasicDetails(space, editor);
        } else {
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

                    return;
                }
            }

            editor.append(Handlebars.compile($('#no-section').html())({}));
        }
    };

    var editBasicDetails = function (space, editor_node) {
        var section_node = newSectionEditor(gettext('basic-edit-title')),
            schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-basic').html()),
            context = {
                name: space.name,
                manager: space.manager,
                types: [],
                editors: space.editors.join(', ')
            },
            i, j, checked, help, help_name;

        for (i = 0; i < schema.type.length; i += 1) {
            checked = '';

            for (j = 0; j < space.type.length; j += 1) {
                if (space.type[j] == schema.type[i]) {
                    checked = 'checked';
                    break;
                }
            }

            console.log('msgid = "' + schema.type[i] + '"');

            help_name = schema.type[i] + '_help';
            help = gettext(help_name);

            context.types.push({
                name: gettext(schema.type[i]),
                value: 'schema.type[i]',
                choice: checked,
                help: help,
                has_help: (help.length > 0 && help != help_name)
            });
        }

        section_node.append($(tpl(context)));

        editor_node.append(section_node);

        $('#input-space-name').keyup(function (e) {
            $('#space-name').html($(e.target).val());
        });
    };

    var editHoursDetails = function (section, editor_node) {
        var section_node = newSectionEditor(section.section),
            anchor_node, key, days, hours, i, j;

        section_node.append($(Handlebars.compile($('#space-edit-hours').html())({})));
        anchor_node = section_node.find('a').parent();
        if (section.hasOwnProperty('available_hours')
            && typeof section.available_hours === 'object'
            && $.isArray(section.available_hours)) {
            days = section.available_hours;

            hours = {};
            for (i = 0; i < days.length; i += 1) {
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

            for (i in hours) {
                anchor_node.before(hoursNode(hours[i]));
            }
        }

        appendSectionFields(section.fields, section_node);

        editor_node.append(section_node);

        $('#space-editor #add-hours').click(function (e) {
            $(e.target).parent().before(hoursNode());
        });
    };

    var hoursNode = function (t) {
        var tpl = Handlebars.compile($('#hours-editor').html()),
            edit_node = $(tpl()),
            select_days = edit_node.find('select#days'),
            select_open = edit_node.find('select#opening-time'),
            select_close = edit_node.find('select#closing-time'),
            i;

        for (i = 0; i < weekdays.length; i += 1) {
            option = $('<option></option>').val(weekdays[i]).html(gettext(weekdays[i]));
            if (t && t.hasOwnProperty('days') && $.inArray(weekdays[i], t.days) > -1) {
                option.attr('selected', 'selected');
            }

            select_days.append(option);
        }

        appendHours(select_open, (t) ? t.hours[0] : null);
        appendHours(select_close, (t) ? t.hours[1] : null);

        if (window.spacescout_admin.is_mobile) {
            // MOBILE: handle multi-day selection and display
            select_days.addClass('form-control day-select');
            select_days.change(function(){
                var selected = $(this).val();

                var list = $.map(selected, function(value) {
                    return(gettext(value));
                });
            
                $(this).siblings(".show-days").html(list.join(", "));
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
            option = $('<option></option>').val(value);

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

        context['thumbnails'] = section['thumbnails'];
        if (context['thumbnails'].length) {
            context['thumbnails'][0]['active'] = 'active';
        }

        section_node.append($(tpl(context)));

        editor_node.append(section_node);
    };

    var editSectionDetails = function (section, editor_node) {
        var section_node = newSectionEditor(section.section);

        appendSectionFields(section.fields, section_node);
        editor_node.append(section_node);
    };

    var newSectionEditor = function (title) {
        var tpl = Handlebars.compile($('#editor-container').html());

        return $(tpl({section: title}));
    };

    var appendSectionFields = function (fields, section) {
        var i;

        for (i = 0; i < fields.length; i += 1) {
            if (typeof fields[i].value === 'object') {
                if ($.isArray(fields[i].value)) {
                    appendFieldList(fields[i], section);
                } else {
                    appendFieldValue(fields[i], section);
                }
            }
        }
    };

    var appendFieldValue = function (field, section) {
        var tpl, vartype, varedit, context, data, i, node, src, choice, group;

        context = {
            name: field.name,
            help: (field.hasOwnProperty('help')) ? gettext(field.help) : ''
        };

        if (field.hasOwnProperty('required')) {
            context.required = field.required;
        }

        // fields we know about
        switch (field.value.key) {
        case 'location.building_name':
            tpl = Handlebars.compile($('#space-edit-select').html());
            context.options = [];
            section.append(tpl(context));
            node = section.find('select').last();

            $.ajax({
                url: '/api/v1/buildings/',
                dataType: 'json',
                success: function (data) {
                    var building = getFieldValue(field.value),
                        option;

                    if (typeof data === 'object' && $.isArray(data)) {
                        for (i = 0; i < data.length; i += 1) {
                            option = $('<option></option>').val(i).html(data[i]);

                            if (building == data[i]) {
                                option.attr('selected', 'selected');
                            }

                            node.append(option);
                        }
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    XHRError(xhr);
                }
            });
            break;
        default:
            vartype = schemaVal(field.value.key);
            varedit = (field.value.hasOwnProperty('edit')) ? field.value.edit: null;
            switch (typeof vartype) {
            case 'string':
                switch (vartype.toLowerCase()) {
                case 'int':
                case 'decimal':
                case 'unicode':
                    if (varedit && varedit.hasOwnProperty('tag') && varedit.tag == 'textarea') {
                        if (varedit.hasOwnProperty('placeholder')) {
                            context.placeholder = gettext(varedit.placeholder);
                        }

                        context.value = getFieldValue(field.value);
                        tpl = Handlebars.compile($('#space-edit-textarea').html());
                    } else {
                        context.inputs = [{ value: getFieldValue(field.value)}];
                        tpl = Handlebars.compile($('#space-edit-input').html());
                    }

                    section.append(tpl(context));
                    break;
                default:
                    break;
                }
                break;
            case 'object':
                if ($.isArray(vartype)) {
                    data = [];
                    if (vartype.length == 1 && vartype[0].toLowerCase() == 'true') {
                        src = '#space-edit-checkboxes';
                        data.push(booleanEditStruct(field.value));
                    } else {
                        if (field.value.hasOwnProperty('edit')
                              && field.value.edit.hasOwnProperty('tag')
                               && field.value.edit.tag == 'select') {
                            src = '#space-edit-select';
                            choice = 'selected';
                            group = null;
                        } else {
                            src = '#space-edit-radio';
                            choice = 'checked';
                            group = field.name;
                        }

                        if (field.value.hasOwnProperty('map')) {
                            for (i in field.value.map) {
                                data.push({
                                    name: gettext(field.value.map[i]),
                                    value: i,
                                    choice: (field.value.value == i) ? choice : '',
                                    group: group
                                });
                            }
                        } else {
                            for (i = 0; i < vartype.length; i += 1) {
                                data.push({
                                    name: gettext(vartype[i]),
                                    value: vartype[i],
                                    choice: (String(field.value.value).toLowerCase() == vartype[i]) ? choice : '',
                                    group: group
                                });
                            }
                        }
                    }

                    context.inputs = data;

                    tpl = Handlebars.compile($(src).html());
                    section.append(tpl(context));
                } else {
                    if (typeof field.value.value === 'boolean') {
                        src = '#space-edit-checkboxes';
                        data = [ booleanEditStruct(field.value) ];
                    } else if (typeof vartype === 'string'
                               && (vartype == 'unicode'
                                   || vartype == 'int'
                                   || vartype == 'decimal')) {
                        src = '#space-edit-input';
                        data = [ {
                            value: getFieldValue(field.value)
                        }];
                    }

                    context.inputs = data;
                    tpl = Handlebars.compile($(src).html());
                    section.append(tpl(context));
                }
                break;
            default:
                break;
            }
        }
    };

    var appendFieldList = function(field, section) {
        var tpl, i, vartype,
            values = [],
            bool = false,
            context = {
                name: field.name,
                help: (field.hasOwnProperty('help')) ? gettext(field.help) : ''
            },
            src_selector;

        if (field.hasOwnProperty('required')) {
            context.required = field.required;
        }

        for (i = 0; i < field.value.length; i += 1) {
            if (i == 0 && typeof field.value[i].value === 'boolean') {
                bool = true;
            } else if (typeof field.value[i].value === 'boolean') {
                if (!bool) {
                    values = [];
                    break;
                }
            } else if (bool) {
                values = [];
                break;
            }

            if (bool) {
                values.push(booleanEditStruct(field.value[i]));
            } else {
                vartype = schemaVal(field.value[i].key);
                if (typeof vartype === 'string'
                    && (vartype == 'unicode'
                        || vartype == 'int'
                        || vartype == 'decimal')) {
                    values.push(getFieldValue(field.value[i]));
                }
            }
        }

        if (bool) {
            src_selector = "#space-edit-checkboxes";
            context.inputs = values;
        } else {
            src_selector = "#space-edit-input";
            context.inputs = [{ value: values.join(', ') }];
        }

        tpl = Handlebars.compile($(src_selector).html());
        section.append(tpl(context));
    };

    var booleanEditStruct = function (v) {
        return {
            choice: v.value ? 'checked' : '',
            name: gettext(v.key),
            value: v.key
        };
    };

    var schemaVal = function (key) {
        var schema = window.spacescout_admin.spot_schema,
            keys = key.split('.'),
            val = '',
            i;

        val = schema[keys[0]];
        for (i = 1; i < keys.length; i += 1) {
            val = val[keys[i]];
        }

        return val;
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