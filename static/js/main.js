$(document).ready(function() {

    $('.fileupload').fileupload()

    window.spacescout_admin = window.spacescout_admin || {};

    // general space functions
    window.spacescout_admin.getFieldValue = function (fv) {
        var i, v, fmt,
            t = [],
            value = function (vo) {
                var rv = '', i, v;

                switch (typeof vo.value) {
                case 'string':
                    rv = gettext(vo.value);
                    break;

                case 'number':
                    rv = String(vo.value);
                    break;

                case 'boolean':
                    rv = (vo.value) ? gettext(vo.key) : null;
                    break;

                case 'object':
                    if ($.isArray(vo.value)) {
                        v = [];
                        for (i = 0; i < vo.value.length; i += 1) {
                            v.push(gettext(vo.value[i]));
                        }

                        rv = v.join(',');
                    }
                    break;

                default:
                    rv = null;
                    break;
                };

                return rv;
            };

        if (fv && typeof fv === 'object') {
            if ($.isArray(fv)) {
                for (i = 0; i < fv.length; i += 1) {
                    if (fv[i].hasOwnProperty('value')) {
                        v = value(fv[i]);
                        if (v) {
                            t.push(v);
                        }
                    }
                }

                return t.join(', ');
            } else if (fv.hasOwnProperty('value')) {
                v = value(fv);
                if (v) {
                    return v;
                }
            }
        }

        return '';
    };

    window.spacescout_admin.modifiedTime = function (date) {
        return (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear()
            + ' ' + window.spacescout_admin.prettyHours(date.getHours()
                                                        + ':' + date.getMinutes());
    };

    window.spacescout_admin.prettyHours = function (hours) {
        var t = hours.match(/^(([01]?\d)|2[0123]):([012345]?\d)$/),
            h, m;

        if (t) {
            h = parseInt(t[1]);
            m = parseInt(t[3]);

            if (m == 0) {
                if (h == 0 || h == 23) {
                    return gettext('midnight');
                } else if (h == 12) {
                    return gettext('noon');
                }
            }

            return ((h > 12) ? (h - 12) : h)
                + ':' + ((m < 10) ? ('0' + m) : m)
                + gettext((h > 11) ? 'pm' : 'am');
        }

        return hours;
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

    var booleanEditStruct = function (v) {
        return {
            choice: v.value ? 'checked' : '',
            name: gettext(v.key),
            key: v.key + ':' + String(v.value),
            value: v.key
        };
    };

    var appendFieldHeader = function (name, help, is_required, section) {
        section.append(Handlebars.compile($('#space-edit-field-header').html())({
            name: name,
            help: help,
            is_required: is_required
        }));
    };

    window.spacescout_admin.appendFieldValue = function (field, getval, section) {
        var required = (field.hasOwnProperty('required') && field.required),
            context = {},
            tpl, vartype, varedit, data, i, node, src, choice, group;

        appendFieldHeader(gettext(field.name),
                          (field.hasOwnProperty('help')) ? gettext(field.help) : '',
                          required,
                          section);

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
                    var building = getval(field.value),
                        option;

                    if (typeof data === 'object' && $.isArray(data)) {
                        for (i = 0; i < data.length; i += 1) {
                            option = $('<option></option>').val(field.value.key).html(data[i]);

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

            if (vartype == undefined) {
                vartype = 'unicode'; //default
            }

            switch (typeof vartype) {
            case 'string':
                switch (vartype.toLowerCase()) {
                case 'int':
                case 'decimal':
                    context.inputs = [{
                        key: field.value.key,
                        value: getval(field.value),
                        class: required ? 'value-required' : ''
                    }];
                    tpl = Handlebars.compile($('#space-edit-number').html());
                    node = $(tpl(context));
                    section.append(node);
                    break;
                case 'unicode':
                    if (varedit && varedit.hasOwnProperty('tag') && varedit.tag == 'textarea') {
                        if (varedit.hasOwnProperty('placeholder')) {
                            context.placeholder = gettext(varedit.placeholder);
                        }

                        context.value = getval(field.value);
                        context.class = required ? 'value-required' : '';
                        tpl = Handlebars.compile($('#space-edit-textarea').html());
                    } else {
                        context.inputs = [{
                            key: field.value.key,
                            value: getval(field.value),
                            placeholder: gettext((varedit && varedit.hasOwnProperty('placeholder')) ? varedit.placeholder : 'text_input'),
                            class: required ? 'value-required' : ''
                        }];
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
                        } else if (field.value.hasOwnProperty('edit')
                              && field.value.edit.hasOwnProperty('multi_select')) {
                            src = '#space-edit-checkboxes';
                            choice = 'checked';
                            group = null;
                        } else {
                            src = '#space-edit-radio';
                            choice = 'checked';
                            group = field.name;
                            if (field.value.hasOwnProperty('edit')
                                && field.value.edit.hasOwnProperty('allow_none')) {
                                data.push({
                                    name: gettext('unset'),
                                    key: field.value.key + ':',
                                    value: field.value.key + ':',
                                    group: group
                                });
                            }
                        }

                        if (field.value.hasOwnProperty('map')) {
                            for (i in field.value.map) {
                                data.push({
                                    name: gettext(field.value.map[i]),
                                    key: field.value.key + ':' + i,
                                    value: field.value.key + ':' + i,
                                    choice: (field.value.value == i) ? choice : '',
                                    class: required ? 'value-required' : '',
                                    group: group
                                });
                            }
                        } else {
                            for (i = 0; i < vartype.length; i += 1) {
                                data.push({
                                    name: gettext(vartype[i]),
                                    key: field.value.key + ':' + vartype[i],
                                    value: field.value.key + ':' + vartype[i],
                                    choice: (String(field.value.value).toLowerCase() == vartype[i]) ? choice : '',
                                    class: required ? 'value-required' : '',
                                    has_help: true,
                                    help: gettext(vartype[i] + '_help'),
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
                    } else if (vartype == 'int' || vartype == 'decimal') {
                        src = '#space-edit-number';
                        data = [ {
                            key: field.value.key,
                            value: getval(field.value)
                        }];
                    } else if (typeof vartype === 'string'
                               || (vartype == 'unicode')) {
                        src = '#space-edit-input';
                        data = [ {
                            key: field.value.key,
                            value: (field.value)
                        }];
                    }

                    context.inputs = data;
                    context.class = required ? 'value-required' : '';
                    tpl = Handlebars.compile($(src).html());
                    section.append(tpl(context));
                }
                break;
            default:
                break;
            }
        }
    };

    window.spacescout_admin.appendFieldList = function(field, getval, section) {
        var vartype, i,
            values = [],
            keys = [],
            placeholder = [],
            bool = false,
            context = {},
            src_selector,
            required = (field.hasOwnProperty('required') && field.required);

        appendFieldHeader(field.name,
                          (field.hasOwnProperty('help')) ? gettext(field.help) : '',
                          required,
                          section);

        if (required) {
            context.class = 'value-required';
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

            keys.push(field.value[i].key);

            if (field.value[i].hasOwnProperty('placeholder')) {
                placeholder.push(field.value[i].placeholder);
            }

            if (bool) {
                values.push(booleanEditStruct(field.value[i]));
            } else {
                vartype = schemaVal(field.value[i].key);
                if (typeof vartype === 'string'
                    && (vartype == 'unicode'
                        || vartype == 'int'
                        || vartype == 'decimal')) {
                    values.push(getval(field.value[i]));
                }
            }
        }

        if (bool) {
            src_selector = "#space-edit-checkboxes";
            context.inputs = values;
        } else {
            src_selector = "#space-edit-input";
            context.inputs = [{
                key: keys.join('|'),
                placeholder: placeholder.join(', '),
                value: values.join(', ')
            }];
        }

        section.append(Handlebars.compile($(src_selector).html())(context));
    };

    window.spacescout_admin.validateInput = function (event) {
        var el = $(event.target),
            key = event.keyCode,
            v = el.val();

        switch (el.prop('type')) {
        case 'number':
            if (key == 8 || key == 9 || key == 27 || key == 13 || key == 16 || key == 17 || key == 18 || key == 91) {
                return;
            }

            if (!event.shiftKey && ((key > 47 && key < 58) || (key > 95 && key < 106))) {
            } else {
                event.preventDefault();
            }
            break;
        case 'text':
            if (v.trim().length <= 2) {
                setInterval(window.spacescout_admin.validateFields, 100);
            }

            break;
        default:
            break;
        }
    };

    window.spacescout_admin.validateFields = function () {
        $('.value-required').each(function () {
            var show_cue = function (node, show) {
                    if (show) {
                        node.children('.required-field-icon').show();
                        node.children('.required-field-text').show();
                    } else {
                        node.children('.required-field-icon').hide();
                        node.children('.required-field-text').hide();
                    }
                },
                set_cue = function (node, show) {
                    var i, n;

                    if (node.prev().is('h4')) {
                        show_cue(node.prev(), show);
                    } else { 
                        for (i = 0; i < 8; i += 1) {
                            n = node.parents().eq(i).prev();
                            if (n.is('h4')) {
                                show_cue(n, show);
                                break;
                            }
                        }
                    }
                };

            switch ($(this).prop('tagName').toLowerCase()) {
            case 'input':
                switch ($(this).attr('type')) {
                case 'radio':
                    set_cue($(this), ($('input[name="' + $(this).attr('name') + '"]:checked').length <= 0));
                    break;
                case 'checkbox':
                    set_cue($(this), ($(this).closest('div.panel').find('input:checked').length <= 0));
                    break;
                case 'text':
                    set_cue($(this), ($(this).val().trim().length == 0));
                    break;
                };
                break;
            case 'textarea':
                set_cue($(this), ($(this).val().trim().length == 0));
                break;
            case 'select':
                break;
            default :
                break;
            };
        });
    };

});