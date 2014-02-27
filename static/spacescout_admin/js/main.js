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
            } else if (h == 23 && m == 59) {
                return gettext('midnight');
            }

            return ((h > 12) ? (h - 12) : ((h == 0) ? '12' : h))
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
                        var div = $(e.target).parent().parent().next('div');
                        div.toggle();
                        if (div.is(':visible')) {
                            div.trigger('displayed');
                        }
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
        if (typeof field.value === 'object') {
            appendFieldHeader(field, section);

            if ($.isArray(field.value)) {
                window.spacescout_admin.appendFieldValueList(field, getval, section);
            } else {
                window.spacescout_admin.appendFieldValueItem(field, getval, section);
            }
        }
    };

    window.spacescout_admin.appendFieldValueItem = function (field, getval, section) {
        var required = (field.hasOwnProperty('required') && field.required),
            context = {},
            input, choice, choice_value,
            input_class = '', tpl, vartype, varedit, data, i, node, src;

        // fields we know about
        switch (field.value.key) {
        case 'location.building_name':
            tpl = Handlebars.compile($('#space-edit-select').html());
            context.name = field.value.key;
            context.options = [];
            node = $(tpl(context));

            if (required) {
                node.addClass(required_class);
            }

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
                            context.name = field.value.key;
                            src = '#space-edit-select';
                            choice = 'selected';
                        } else if (field.value.hasOwnProperty('edit')
                              && field.value.edit.hasOwnProperty('multi_select')) {
                            src = '#space-edit-checkboxes';
                            choice = 'checked';
                            if (field.value.edit.hasOwnProperty('limit')) {
                                input_class = 'required-limit-' + field.value.edit.limit;
                            }
                        } else {
                            src = '#space-edit-radio';
                            choice = 'checked';
                            if (field.value.hasOwnProperty('edit')
                               && field.value.edit.hasOwnProperty('default')) {
                                choice_value = field.value.edit.default;
                                if (choice_value == null) {
                                    choice_value = '';
                                }
                            }
                        }

                        if (field.value.hasOwnProperty('map')) {
                            for (i in field.value.map) {
                                var value = field.value.map[i].value,
                                    display = field.value.map[i].display;

                                input = {
                                    text: gettext(display),
                                    key: field.value.key,
                                    value: value,
                                    class: input_class
                                };

                                if (field.value.value == value
                                    || (typeof choice_value !== 'undefined'
                                        && choice_value == value)) {
                                    input.choice =  choice;
                                }

                                if (required) {
                                    input.class = required_class +  ' ' + input.class;
                                }

                                if (field.value.hasOwnProperty('edit')
                                    && field.value.edit.hasOwnProperty('requires')) {
                                    input.class = dependent_prefix + field.value.edit.requires + ' ' + input.class;
                                }

                                data.push(input);
                            }
                        } else {
                            for (i = 0; i < vartype.length; i += 1) {
                                input = {
                                    text: gettext(vartype[i]),
                                    key: field.value.key,
                                    value: vartype[i],
                                    class: input_class,
                                    has_help: true,
                                    help: gettext(vartype[i] + '_help')
                                };

                                if (required) {
                                    input.class = required_class +  ' ' + input.class;
                                }

                                if (field.value.hasOwnProperty('edit')
                                    && field.value.edit.hasOwnProperty('requires')) {
                                    input.class = dependent_prefix + field.value.edit.requires + ' ' + input.class;
                                }

                                if (((typeof field.value.value === 'object')
                                           && $.isArray(field.value.value)
                                           && $.inArray(vartype[i], field.value.value) >= 0)
                                          || String(field.value.value).toLowerCase() == vartype[i]) {
                                    input.choice = choice;
                                }

                                data.push(input);
                            }
                        }
                    }

                    context.inputs = data;

                    tpl = Handlebars.compile($(src).html());
                    node = $(tpl(context));
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

    window.spacescout_admin.appendFieldValueList = function(field, getval, section) {
        var vartype, i,
            values = [],
            values_length,
            keys = [],
            placeholder = [],
            bool = false,
            context = {},
            src_selector,
            required = (field.hasOwnProperty('required') && field.required);

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
                value: values_length ? values.join(', ') : '',
                placeholder: placeholder.join(', '),
                class: (required) ? required_class : ''
            }];
        }

        section.append(Handlebars.compile($(src_selector).html())(context));
    };

    var booleanEditStruct = function (v) {
        return {
            choice: v.value ? 'checked' : '',
            text: gettext(v.key),
            key: v.key
        };
    };

    window.spacescout_admin.businessHours = function (available_hours) {
        var periods = [],
            runs = {},
            context, h, i, l, n, r, d, s;

        for (d = 0; d < 7; d += 1) {
            if (available_hours[d].hasOwnProperty('hours')) {
                h = available_hours[d].hours;

                for (i = 0; i < h.length; i++) {
                    if (h[i][0] == '00:00' && h[i][1] == '23:59') {
                        s = gettext('allday');
                    } else {
                        s = window.spacescout_admin.prettyHours(h[i][0])
                            + ' - ' + window.spacescout_admin.prettyHours(h[i][1]);
                    }

                    if (runs.hasOwnProperty(s)) {
                        runs[s].push(d);
                    } else {
                        runs[s] = [d];
                    }
                }
            }
        }

        for (r in runs) {
            context = {
                day: gettext(available_hours[runs[r][0]].day),
                hours: r
            };

            l = runs[r].length;
            n = runs[r][0] + 1;
            h = 0;
            for (i = 1; i <= l; i += 1) {
                if (i < l && runs[r][i] == n) {
                    n += 1;
                    h += 1;
                } else {
                    if (h > 0) {
                        context.day +=  ((h > 1) ? ' - ' : ', ')  + gettext(available_hours[runs[r][i-1]].day);
                    }

                    if (i < l) {
                        context.day +=  ', ' + gettext(available_hours[runs[r][i]].day);
                        n = runs[r][i] + 1;
                    }

                    h = 0;
                }
            }

            periods.push(context);
        }

        return periods;
    };

    window.spacescout_admin.validateInput = function (event) {
        var el = $(event.target),
            key = event.which,
            v = el.val().trim(),
            min = el.attr('min') ? parseInt(el.attr('min')) : undefined;
        
        switch (el.attr('type')) {
        case 'number':
            if (min && min < 0 && key == 189) {
                if (v.charAt(0) != '-') {
                    el.val('-' + v);
                }

                event.preventDefault();
            } else if (!window.spacescout_admin.isNumberInput(event)
                       || (min != undefined && parseInt(v + String.fromCharCode(key)) < min)) {
                event.preventDefault();
            }

        case 'text':
            setInterval(function () {
                window.spacescout_admin.validateFields();
            }, 100);
            break;
        default:
            break;
        }
    };

    window.spacescout_admin.validateFields = function () {
        var show_cue = function (n, s) {
                var req_node = $('.' + required_class, n);

                if (!req_node.length) {
                    $('small', n).before($(Handlebars.compile($('#space-edit-field-required').html())()));
                    req_node = $('.' + required_class, n);
                }

                if (s) {
                    req_node.show();
                } else {
                    req_node.hide();
                }
            },
            set_cue = function (node, show) {
                var h = node.prevAll('.field-header');

                if (h.length) {
                    show_cue(h.eq(0), show);
                } else {
                    node.parents().prevAll('.field-header').each(function () {
                        show_cue($(this), show);
                        return false;
                    });
                }
            },
            set_cue_by_element_type = function(el) {
                var cue, selected;

                switch (el.prop('tagName').toLowerCase()) {
                case 'input':
                    switch (el.attr('type')) {
                    case 'radio':
                        cue = ($('input[name="' + el.attr('name') + '"]:checked').length <= 0);
                        break;
                    case 'checkbox':
                        cue = (el.closest('div.panel').find('input:checked').length <= 0);
                        break;
                    case 'number':
                    case 'text':
                        if (el.attr('name').indexOf('|') >= 0) {
                            cue = (multiValueInput(el) == null);
                            break;
                        }

                        cue = (el.val().trim().length == 0);
                        break;
                    };
                    break;
                case 'textarea':
                    cue = (el.val().trim().length == 0);
                    break;
                case 'select':
                    selected = $(this).find('option:selected');
                    cue = (selected.length == 0 || selected.val().length == 0);
                    break;
                default :
                    break;
                };

                if (cue !== undefined) {
                    set_cue(el, cue);
                }

                return cue;
            };

        // required fields
        $('.' + required_class).each(function () {
            set_cue_by_element_type($(this));
        });

        // fields that dependent on another
        $('input[class^="' + dependent_prefix + '"]:checked').each(function () {
            var el = $(this),
                el_value = el.attr('value'),
                m = el.attr('class').slice(dependent_prefix.length).match(/([^\s]+)(\s|$)/),
                target_el, has_cue;

            if (m) {
                target_el = $('*[name="' + m[1] + '"]');
                if (typeof el_value !== 'undefined' && el_value !== false) {
                    if (el_value.length == 0 || el_value == 'null' || el_value.toLowerCase() == 'false') {
                        set_cue(target_el, false);
                        if (target_el.hasClass(required_class)) {
                            target_el.removeClass(required_class);
                        }
                    } else {
                        has_cue = set_cue_by_element_type(target_el);
                        if (has_cue == true) {
                            if (!target_el.hasClass(required_class)) {
                                target_el.addClass(required_class);
                            }
                        } else if (has_cue == false) {
                            if (target_el.hasClass(required_class)) {
                                target_el.removeClass(required_class);
                            }
                        }
                    }
                } else {
                    set_cue(target_el, true);
                }
            }
        });

        // fields with specific format
        $('input[name="location.latitude|location.longitude"]').each (function () {
            set_cue($(this), window.spacescout_admin.isValidLatLong($(this).val()) == null);
        });
    };

    window.spacescout_admin.isValidLatLong = function (val) {
        return val.trim().match(/^([-]?\d+)(.\d{0,6})?\d*?\s*,\s*([-]?\d+)(.\d{0,6})?\d*?$/);
    };

    window.spacescout_admin.isNumberInput = function (event) {
        var key = event.which,
            allowed = [8, 9, 27, 13, 16, 17, 18, 37, 39, 91, 188];

        return (event.ctrlKey
                || allowed.indexOf(key) >= 0
                || (!event.shiftKey && (key > 47 && key < 58)));
    };

    window.spacescout_admin.collectInput = function () {
        var data = {};

        $('input, textarea').each(function () {
            var key = $(this).attr('name'),
                value,
                checked = $(this).is(':checked'),
                p, q, i;

            switch ($(this).prop('type')) {
            case 'checkbox':
                value = $(this).attr('value');

                if (typeof value !== 'undefined' && value !== false && value.length) {
                    if (checked) {
                        if (data.hasOwnProperty(key)) {
                            if (typeof(data[key]) == 'object' && $.isArray(data[key])) {
                                data[key].push(value);
                            } else {
                                data[key] = [data[key], value];
                            }
                        } else {
                            data[key] = value;
                        }
                    }
                } else {
                    data[key] = checked;
                }

                break;
            case 'radio':
                value = $(this).attr('value');

                if (checked) {
                    if (typeof value !== 'undefined' && value !== false) {
                        data[key] = value;
                    } else {
                        data[key] = checked;
                    }
                }

                break;
            case 'text':
                p = isMultiValueInput($(this));
                if (p) {
                    if ($(this).attr('name') == 'location.latitude|location.longitude') {
                        value = window.spacescout_admin.isValidLatLong($(this).val().trim());
                        if (value) {
                            data['location.latitude'] = value[1] + ((value[2]) ? value[2] : '');
                            data['location.longitude'] = value[3] + ((value[4]) ? value[4] : '');
                        }
                        else {
                            // Just drop bad data?  this works for an empty field
                            // value, but if they enter 12.1234, what's their
                            // expectation?
                            data['location.latitude'] = null;
                            data['location.longitude'] = null;
                        }
                    } else {
                        q = getMultiValues(p, $(this).val().trim());
                        for (i = 0; i < p.length; i += 1) {
                            data[p[i]] = q ? q[p[i]] : '';
                        }
                    }

                    break;
                }
                // ELSE fall thru and set simple value
            default:
                if (key) {
                    data[key] = $(this).val().trim();
                }

                break;
            }
        });

        $('select option:selected').each(function () {
            var key = $(this).parent().attr('name'),
                value = $(this).attr('value');

            if (key) {
                if (value && value.length) {
                    data[key] = value;
                } else {
                    data[key] = $(this).text();
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
