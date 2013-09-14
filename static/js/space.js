$(document).ready(function() {

    (function () {
        $.ajax({
            url: '/api/v1/space/' + window.spacescout_admin.spot_id,
            dataType: 'json',
            success: function (data) {
                var tpl, context, section, html, i, incomplete;

                $('.space-content-loading').hide();

                for (i = 0; i < data.sections.length; i += 1) {
                    section = data.sections[i];
                    context = {
                        section: gettext(section.section),
                        edit_url: '/edit/' + window.spacescout_admin.spot_id
                            + '/#' + encodeURIComponent(section.section)
                    };

                    if (i == 0) { // basic section
                        context.name = gettext(data.name);
                        context.fields = prepSectionFields(section.fields.slice(1));
                        tpl = Handlebars.compile($('#space-details').html());
                        $('.space-detail-header').append(tpl(context));
                        tpl = Handlebars.compile($('#space-section-fields').html());
                        $('.space-detail-header').append(tpl(context));
                    } else {
                        switch (section.section) {
                        case 'hours':
                            context['available_hours'] = contextAvailableHours(section['available_hours']);
                            context.fields = prepSectionFields(section.fields);
                            html = $(Handlebars.compile($('#space-section-hours').html())(context));
                            break;
                        case 'images':
                            context['thumbnails'] = section['thumbnails'];
                            if (context['thumbnails'].length) {
                                context['thumbnails'][0]['active'] = 'active';
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

                        html.insertAfter('.space-detail-section:last');
                    }
                }

                // validation cues
                incomplete = incompleteFields();
                if (incomplete && incomplete.length) {
                    $(Handlebars.compile($('#incomplete-items').html())({
                        incomplete: incomplete
                    })).insertAfter('.space-detail-section:last');
                }

                // actions
                $(Handlebars.compile($('#space-actions').html())({
                    is_complete: !(incomplete && incomplete.length),
                    is_modified: false,
                    is_published: false,
                    modified_by: (data.modified_by.length) ? data.modified_by : gettext('unknown'),
                    last_modified: window.spacescout_admin.modifiedTime(new Date(data.last_modified))
                })).insertAfter('.space-detail-section:last');
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
            j, d, h, s;

        for (d = 0; d < 7; d += 1) {
            h = [];
            if (available_hours[d].hasOwnProperty('hours')) {
                var hours = available_hours[d].hours;
                if (hours.length) {
                    for (j = 0; j < hours.length; j++) {
                        h.push(window.spacescout_admin.prettyHours(hours[j][0])
                               + ' - ' + window.spacescout_admin.prettyHours(hours[j][1]));
                    }
                }
            }

            s = (h.length) ? h.join(', ') : 'none';

            if (d == 0 || !runs.hasOwnProperty(s)) {
                runs[s] = {
                    'start': d,
                    'end': d
                };
            } else {
                runs[s].end = d;
            }
        }

        for (d = 0; d < 7; d += 1) {
            for (j in runs) {
                if (runs[j].start == d && j != 'none') {
                    switch (runs[j].end - runs[j].start) {
                    case 0:
                        periods.push({
                            day: gettext(available_hours[runs[j].start].day),
                            hours: j
                        });
                        break;
                    case 1:
                        periods.push({
                            day: gettext(available_hours[runs[j].start].day),
                            hours: j
                        });
                        periods.push({
                            day: gettext(available_hours[runs[j].end].day),
                            hours: j
                        });
                        break;
                    default:
                        periods.push({
                            day: gettext(available_hours[runs[j].start].day)
                                + ' - ' + gettext(available_hours[runs[j].end].day),
                            hours: j
                        });
                        break;
                    }
                    break;
                }
            }
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