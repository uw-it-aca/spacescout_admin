$(document).ready(function() {

    var required_class = 'required-field';
    var dependent_prefix = 'required-key-';

    $('.fileupload').fileupload();

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

                        rv = v.join(', ');
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
                        if (v && v.length) {
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

    var appendFieldHeader = function (field, section) {
        var tpl = Handlebars.compile($('#space-edit-field-header').html()),
            header_node = $(tpl({
                name: gettext(field.name)
            })),
            node,
            link,
            s;

        section.append(header_node);

        if ((field.hasOwnProperty('required') && field.required)) {
            tpl = Handlebars.compile($('#space-edit-field-required').html());
            header_node.append(tpl());
        }

        if (field.hasOwnProperty('help')) {
            if (field.help.hasOwnProperty('text')) {
                tpl = Handlebars.compile($('#space-edit-field-help').html());
                node = $(tpl({
                    help: gettext(field.help.text)
                }));
            }

            if (node) {
                if (field.help.hasOwnProperty('expanded')) {
                    s = gettext(field.help.expanded.hasOwnProperty('link') ? field.help.expanded.link :'more');
                    node.append(' ');
                    link = $('<a></a>').prop('href', 'javascript:void(0);').html(s);
                    link.click(function (e) {
                        $(e.target).parent().parent().next('div').toggle();
                    });

                    node.append(link);
                    header_node.append(node);

                    tpl = Handlebars.compile($('#space-edit-field-more-help').html());
                    node = $(tpl({
                        more_help: gettext(field.help.expanded.text)
                    }));
                    node.insertAfter(header_node);
                } else {
                    header_node.append(node);
                }
            }
        }
    };

    window.spacescout_admin.appendFieldValue = function (field, getval, section) {
        var required = (field.hasOwnProperty('required') && field.required),
            context = {},
            choice, has_choice = false,
            name = null,
            chosen,
            input_class, tpl, vartype, varedit, data, i, node, src,  group;

        appendFieldHeader(field, section);

        // fields we know about
        switch (field.value.key) {
        case 'location.building_name':
            tpl = Handlebars.compile($('#space-edit-select').html());
            context.options = [];
            node = $(tpl(context));
            if (field.value.hasOwnProperty('edit') && field.value.edit.hasOwnProperty('dependency')) {
                node.addClass('campus-buildings');
            }

            section.append(node);
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
                        class: required ? required_class : ''
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

                        context.key = field.value.key;
                        context.value = getval(field.value);
                        context.class = required ? required_class : '';
                        tpl = Handlebars.compile($('#space-edit-textarea').html());
                    } else {
                        context.inputs = [{
                            key: field.value.key,
                            value: getval(field.value),
                            placeholder: gettext((varedit && varedit.hasOwnProperty('placeholder')) ? varedit.placeholder : 'default_placeholder'),
                            class: required ? required_class : ''
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
                            name = field.value.key;
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
                                if (!has_choice && (field.value.value == i)) {
                                    has_choice = true;
                                }

                                input_class = required ? required_class : '';
                                if (field.value.hasOwnProperty('edit')
                                    && field.value.edit.hasOwnProperty('requires')) {
                                    input_class = dependent_prefix + field.value.edit.requires + ' ' + input_class;
                                }

                                data.push({
                                    name: gettext(field.value.map[i]),
                                    key: field.value.key + ':' + i,
                                    value: field.value.key + ':' + i,
                                    choice: (field.value.value == i) ? choice : '',
                                    class: input_class,
                                    group: group
                                });
                            }
                        } else {
                            for (i = 0; i < vartype.length; i += 1) {
                                if (!has_choice && (String(field.value.value).toLowerCase() == vartype[i])) {
                                    has_choice = true;
                                }

                                input_class = required ? required_class : '';
                                if (field.value.hasOwnProperty('edit')
                                    && field.value.edit.hasOwnProperty('requires')) {
                                    input_class = dependent_prefix + field.value.edit.requires + ' ' + input_class;
                                }

                                chosen = (((typeof field.value.value === 'object')
                                           && $.isArray(field.value.value)
                                           && $.inArray(vartype[i], field.value.value) >= 0)
                                          || String(field.value.value).toLowerCase() == vartype[i]);
                                
                                data.push({
                                    name: gettext(vartype[i]),
                                    key: field.value.key + ':' + vartype[i],
                                    value: field.value.key + ':' + vartype[i],
                                    choice: (chosen) ? choice : '',
                                    class: input_class,
                                    has_help: true,
                                    help: gettext(vartype[i] + '_help'),
                                    group: group
                                });
                            }
                        }

                        if (!has_choice && (field.value.hasOwnProperty('edit')
                                            && field.value.edit.hasOwnProperty('allow_none'))) {
                            data[0].choice = choice;
                        }
                    }

                    context.inputs = data;

                    tpl = Handlebars.compile($(src).html());
                    node = $(tpl(context));
                    if (name) {
                        node.attr('name', name);
                    }

                    section.append(node);
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
                    context.class = required ? required_class : '';
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
            values_length,
            keys = [],
            placeholder = [],
            bool = false,
            context = {},
            src_selector,
            required = (field.hasOwnProperty('required') && field.required);

        appendFieldHeader(field, section);

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

            if (field.value[i].hasOwnProperty('edit')
                && field.value[i].edit.hasOwnProperty('placeholder')) {
                placeholder.push(field.value[i].edit.placeholder);
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
            values_length = 0;
            for (i = 0; i < values.length; i += 1) {
                values_length += values[i].trim().length; 
            }

            src_selector = "#space-edit-input";
            context.inputs = [{
                key: keys.join('|'),
                placeholder: placeholder.join(', '),
                class: (required) ? required_class : '',
                value: values_length ? values.join(', ') : ''
            }];
        }

        section.append(Handlebars.compile($(src_selector).html())(context));
    };

    var booleanEditStruct = function (v) {
        return {
            choice: v.value ? 'checked' : '',
            name: gettext(v.key),
            key: v.key,
            value: v.key
        };
    };

    window.spacescout_admin.validateInput = function (event) {
        var el = $(event.target),
            key = event.keyCode,
            v = el.val(),
            multi = ($.inArray('|') >= 0);

        switch (el.prop('type')) {
        case 'number':
            if (key == 8 || key == 9 || key == 27 || key == 13 || key == 16 || key == 17 || key == 18 || key == 91) {
                return;
            }

            if (!(!event.shiftKey && ((key > 47 && key < 58) || (key > 95 && key < 106)))) {
                event.preventDefault();
            }

        case 'text':
            setInterval(window.spacescout_admin.validateFields, 100);
            break;
        default:
            break;
        }
    };

    window.spacescout_admin.validateFields = function () {
        var show_cue = function (n, s) {
                var req_node = n.find('.' + required_class);

                if (!req_node.length) {
                    var tpl = Handlebars.compile($('#space-edit-field-required').html());
                    req_node = $(tpl());
                    $(':first', n).prepend(req_node);
                }

                if (s) {
                    req_node.show();
                } else {
                    req_node.hide();
                }
            },
            set_cue = function (node, show) {
                var i, n;

                if (node.prev().hasClass('field-header')) {
                    show_cue(node.prev(), show);
                } else { 
                    for (i = 0; i < 8; i += 1) {
                        n = node.parents().eq(i).prev();
                        if (n.hasClass('field-header')) {
                            show_cue(n, show);
                            break;
                        }
                    }
                }
            };

        $('.' + required_class).each(function () {
            var el = $(this);

            switch (el.prop('tagName').toLowerCase()) {
            case 'input':
                switch (el.attr('type')) {
                case 'radio':
                    set_cue(el, ($('input[name="' + el.attr('name') + '"]:checked').length <= 0));
                    break;
                case 'checkbox':
                    set_cue(el, (el.closest('div.panel').find('input:checked').length <= 0));
                    break;
                case 'number':
                case 'text':
                    if (el.attr('name').indexOf('|') >= 0) {
                        set_cue(el, (multiValueInput(el) == null));
                        break;
                    }

                    set_cue(el, (el.val().trim().length == 0));
                    break;
                };
                break;
            case 'textarea':
                set_cue(el, (el.val().trim().length == 0));
                break;
            case 'select':
                break;
            default :
                break;
            };
        });

        $('input[class^="' + dependent_prefix + '"]:checked').each(function () {
            var el = $(this),
                p = keyValuePair(el.val()),
                m = el.prop('class').slice(dependent_prefix.length).match(/([^\s]+)(\s|$)/),
                target_el;

            if (m) {
                target_el = $('*[name="' + m[1] + '"]');
                if (p) {
                    if (p.value == 'null' || p.value.toLowerCase() == 'false') {
                        set_cue(target_el, false);
                        if (target_el.hasClass(required_class)) {
                            target_el.removeClass(required_class);
                        }
                    } else if (target_el.val().trim().length == 0) {
                        set_cue(target_el, true);
                        if (!target_el.hasClass(required_class)) {
                            target_el.addClass(required_class);
                        }
                    }
                } else {
                    set_cue(target_el, true);
                }
            }
        });
    };

    window.spacescout_admin.collectInput = function () {
        var data = {};

        $('input, textarea').each(function () {
            var v = $(this).val().trim(),
                checked = $(this).is(':checked'),
                p, q, i;

            switch ($(this).prop('type')) {
            case 'checkbox':
                p = keyValuePair(v);

                if (p) {
                    if (checked) {
                        if (data.hasOwnProperty(p.key)) {
                            if (typeof(data[p.key]) == 'object'
                                && $.isArray(data[p.key])) {
                                data[p.key].push(p.value);
                            } else {
                                data[p.key] = [data[p.key], p.value];
                            }
                        } else {
                            data[p.key] = p.value;
                        }
                    }
                } else {
                    data[v] = checked;
                }

                break;
            case 'radio':
                if (checked) {
                    p = keyValuePair(v);

                    if (p) {
                        data[p.key] = p.value;
                    } else {
                        data[v] = checked;
                    }
                }

                break;
            case 'text':
                p = isMultiValueInput($(this));
                if (p) {
                    q = getMultiValues(p, v);
                    for (i = 0; i < p.length; i += 1) {
                        data[p[i]] = q ? q[p[i]] : '';
                    }

                    break;
                }
                // ELSE fall thru and set simple value
            default:
                p = $(this).attr('name');
                if (p) {
                    data[p] = v;
                }
                break;
            }
        });

        $('select option:selected').each(function () {
            var node = $(this),
                v, p;

            if (!node.hasClass('hours-value')) {
                v = node.val().trim(),
                p = keyValuePair(v);

                if (p) {
                    data[p.key] = p.value;
                } else {
                    data[v] = $(this).text();
                }
            }
        });

        $('.business-hours').each(function ()  {
            var open,
                close,
                open_v,
                close_v,
                normalize = function (h) {
                    return (h == '24:00' ? '23:59' : h);
                };

            open = normalize($('#hours-open', this).val());
            close = normalize($('#hours-close', this).val());

            if (open && close) {
                open_v = parseInt(open.split(':').join(''));
                close_v = parseInt(close.split(':').join(''));

                if (open < close) {
                    $('select#days option:selected', this).each(function () {
                        var day = $(this).val();

                        if (!data.hasOwnProperty('available_hours')) {
                            data['available_hours'] = {};
                        }

                        if (data['available_hours'].hasOwnProperty(day)) {
                            data['available_hours'][day].push([open, close]);
                        } else {
                            data['available_hours'][day] = [[open, close]];
                        }
                    });
                }
            }
        });

        return data;
    };

    var keyValuePair = function (s) {
        var m = s.match(/^([^:]+):(.*)$/);
        return m ? { key: m[1], value: m[2] } : null;
    };

    var multiValueInput = function (input) {
        return getMultiValues(isMultiValueInput(input), input.val().trim());
    };

    var isMultiValueInput = function (input) {
        var ka = input.attr('name').match(/(([^|]+)(|$))/g),
            data = [], i;

        if (ka && ka.length > 1) {
            for (i = 0; i < ka.length; i += 1) {
                data.push(ka[i]);
            }

            return data;
        }

        return null;
    };

    var getMultiValues = function (keys, value) {
        var values = value.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g),
            data = {}, i;

        if (values && keys.length > 1 && values.length == keys.length) {
            for (i = 0; i < keys.length; i += 1) {
                data[keys[i]] = values[i];
            }

            return data;
        }

        return null;
    };
});
