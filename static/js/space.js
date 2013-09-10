$(document).ready(function() {

    (function () {
        $.ajax({
            url: '/api/v1/space/' + window.spacescout_admin.spot_id,
            dataType: 'json',
            success: function (data) {
                var tpl, context, section, field, html, e, h, i, j, d, runs, s;

                $('.space-content-loading').hide();

                tpl = Handlebars.compile($('#space-details').html());
                html = tpl({
                    id: window.spacescout_admin.spot_id,
                    name: data.name,
                    type: listToString(data.type),
                    manager: data.manager,
                    editors: ''
                });

                $('.space-detail-header').append(html);
                $('.space-detail-header > div > a').click(function () {
                    window.location = '/edit/' + window.spacescout_admin.spot_id + '/#basic';
                });

                for (i in data.sections) {
                    section = data.sections[i];
                    context = {
                        section: section.section,
                        edit_url: '/edit/' + window.spacescout_admin.spot_id
                            + '/#' + encodeURIComponent(section.section)
                    };

                    if (section.section == 'hours') {
                        context['available_hours'] = [];
                        runs = {};
                        for (d = 0; d < 7; d += 1) {
                            h = [];
                            if (section['available_hours'][d].hasOwnProperty('hours')) {
                                var hours = section['available_hours'][d].hours;
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
                                        context.available_hours.push({
                                            day: gettext(section['available_hours'][runs[j].start].day),
                                            hours: j
                                        });
                                        break;
                                    case 1:
                                        context.available_hours.push({
                                            day: gettext(section['available_hours'][runs[j].start].day),
                                            hours: j
                                        });
                                        context.available_hours.push({
                                            day: gettext(section['available_hours'][runs[j].end].day),
                                            hours: j
                                        });
                                        break;
                                    default:
                                        context.available_hours.push({
                                            day: gettext(section['available_hours'][runs[j].start].day)
                                                + ' - ' + gettext(section['available_hours'][runs[j].end].day),
                                            hours: j
                                        });
                                        break;
                                    }
                                    break;
                                }
                            }
                        }

                        context.fields = prepSectionFields(section);

                        tpl = Handlebars.compile($('#space-section-hours').html());
                        html = tpl(context);
                        
                    } else if (section.section == 'images') {
                        context['thumbnails'] = section['thumbnails'];
                        if (context['thumbnails'].length) {
                            context['thumbnails'][0]['active'] = 'active';
                        }
                        tpl = Handlebars.compile($('#space-section-images').html());
                        html = tpl(context);
                    } else {
                        context.fields = prepSectionFields(section);
                        tpl = Handlebars.compile($('#space-section').html());
                        html = tpl(context);
                    }

                    // insert html in section order
                    e = $('.space-detail-header');
                    for (j = 0; j < i; j++) {
                        e = e.next();
                    }

                    e.after(html);
                }
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

    var prepSectionFields = function (section) {
        var fields = [],
            s, field;

        if (section.hasOwnProperty('fields')) {
            for (s in section.fields) {
                field = section.fields[s];
                fields.push({
                    name: field.name,
                    has_name: (field.name.length > 0),
                    value: getFieldValue(field),
                    required: field.hasOwnProperty('required') ? field.required == true : false
                });
            }
        }

        return fields;
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