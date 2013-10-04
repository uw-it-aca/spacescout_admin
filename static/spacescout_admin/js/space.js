$(document).ready(function() {

    (function () {
        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/space/' + window.spacescout_admin.space_id,
            dataType: 'json',
            success: function (data) {
                var tpl, context, section, html, i, incomplete;

                $('.space-content-loading').hide();
                html = $(Handlebars.compile($('#space-details').html())({ name: data.name }));
                $('.space-content-loading').siblings(':last').after(html);

                for (i = 0; i < data.sections.length; i += 1) {
                    section = data.sections[i];
                    context = {
                        section: gettext(section.section),
                        edit_url: window.spacescout_admin.app_url_root + 'edit/' + window.spacescout_admin.space_id
                            + '/#' + encodeURIComponent(section.section)
                    };

                    switch (section.section) {
                    case 'hours_access':
                        context['available_hours'] = contextAvailableHours(section['available_hours']);
                        context.fields = prepSectionFields(section.fields);
                        html = $(Handlebars.compile($('#space-section-hours').html())(context));
                        break;
                    case 'images':
                        context['images'] = section['images'];
                        if (context['images'].length) {
                            context['images'][0]['active'] = 'active';
                        }
                        html = $(Handlebars.compile($('#space-section-images').html())(context));
                        break;
                    default:
                        context.fields = prepSectionFields(section.fields);
                        html = $(Handlebars.compile($('#space-section').html())(context));
                        tpl = Handlebars.compile($('#space-section-fields').html());
                        html.append(tpl(context));
                        break;
                    }

                    $('.space-content-loading').siblings(':last').after(html);
                }

                // validation cues
                incomplete = incompleteFields();
                if (incomplete && incomplete.length) {
                    html = $(Handlebars.compile($('#incomplete-items').html())({
                        incomplete: incomplete
                    }));

                    $('.space-content-loading').siblings(':last').after(html);
                }

                // actions
                html = $(Handlebars.compile($('#space-actions').html())({
                    is_complete: !(incomplete && incomplete.length),
                    is_modified: false,
                    is_published: false,
                    modified_by: (data.modified_by.length) ? data.modified_by : gettext('unknown'),
                    last_modified: window.spacescout_admin.modifiedTime(new Date(data.last_modified))
                }));

                $('.space-content-loading').siblings(':last').after(html);
            },
            error: function (xhr, textStatus, errorThrown) {
                var json;

                try {
                    json = $.parseJSON(xhr.responseText);
                    console.log('space query service error:' + json.error);
                } catch (e) {
                    console.log('Unknown space service error: ' + xhr.responseText);
                }
            }
        });
    }());

    var prepSectionFields = function (fields) {
        var contexts = [],
            i, field, value;

        for (i = 0; i < fields.length; i += 1) {
            field = fields[i];
            value = getFieldValue(field);
            contexts.push({
                name: gettext(field.name),
                has_name: (field.name.length > 0),
                value: value,
                is_missing: (field.hasOwnProperty('required')
                             && field.required
                             && (!value
                                 || value == ''
                                 || value.toLowerCase() == gettext('noinfo').toLowerCase()))
            });
        }

        return contexts;
    };

    var contextAvailableHours = function (available_hours) {
        var periods = [],
            runs = {},
            context, h, i, l, n, r, d, s;

        for (d = 0; d < 7; d += 1) {
            if (available_hours[d].hasOwnProperty('hours')) {
                h = available_hours[d].hours;

                for (i = 0; i < h.length; i++) {
                    s = window.spacescout_admin.prettyHours(h[i][0])
                        + ' - ' + window.spacescout_admin.prettyHours(h[i][1]);
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
            h = null;
            for (i = 1; i < l; i += 1) {
                if (runs[r][i] == n) {
                    n += 1;
                    h = i;
                    d = !(i < (l - 1));
                } else {
                    d = true;
                }

                if (d) {
                    if (h) {
                        context.day += ' - ' + gettext(available_hours[runs[r][h]].day);
                        n = runs[r][i] + 1;
                    }

                    if (!h || h != i) {
                        context.day += ', ' + gettext(available_hours[runs[r][i]].day);
                    }

                    h = null;
                }
            }

            periods.push(context);
        }

        return periods;
    };

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

    var incompleteFields = function () {
        var incomplete = [];

        $('.required-field').each(function () {
            incomplete.push({
                field: $(this).parent().contents().eq(0).text().trim(),
                edit_url: $(this).closest('.space-detail-section').find('div.section-edit a').attr('href')
            });
        });

        return incomplete;
    };

    var listToString = function(list) {
        var i, t = [];

        for (i = 0; i < list.length; i += 1) {
            switch (typeof list[i]) {
            case 'string':
                t.push(gettext(list[i]));
                break;
            case 'number':
                t.push(String(list[i]));
                break;
            case 'object':
                if ($.isArray(list[i])) {
                    t.push(listToString(list[i]));
                }
                break;
            default:
                break;
            }
        }

        return t.join(', ');
    };

    var getFieldValue = function (f) {
        var v;

        if (f.hasOwnProperty('value') && typeof f.value === 'object') {
            v = window.spacescout_admin.getFieldValue(f.value);

            if (f.value.hasOwnProperty('map') && f.value.map.hasOwnProperty(v)) {
                v = gettext(f.value.map[v]);
            }

            if (((typeof v != 'string') || v.length > 0) && f.value.hasOwnProperty('format')) {
                v = f.value.format.replace('\{0\}', v);
            }

            if (v.length) {
                return v;
            }
        }

        return gettext('noinfo');
    };

});
