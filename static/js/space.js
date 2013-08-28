$(document).ready(function() {

    // fetch spot schema
    (function () {
        $.ajax({
            url: '/api/v1/space/' + window.spacescout_admin.spot_id,
            dataType: 'json',
            success: function (data) {
                var tpl, context, section, field, html, e, h, i, j, d, runs, s;

                tpl = Handlebars.compile($('#space-details').html());
                html = tpl({
                    name: data.name,
                    type: data.type,
                    manager: data.manager,
                    editors: ''
                });

                $('.space-detail-header').append(html);

                for (i in data.sections) {
                    section = data.sections[i];
                    context = {
                        section: section.section
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
                                        h.push(_prettyHours(hours[j][0])
                                               + ' - ' + _prettyHours(hours[j][1]));
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
                                            day: section['available_hours'][runs[j].start].day,
                                            hours: j
                                        });
                                        break;
                                    case 1:
                                        context.available_hours.push({
                                            day: section['available_hours'][runs[j].start].day,
                                            hours: j
                                        });
                                        context.available_hours.push({
                                            day: section['available_hours'][runs[j].end].day,
                                            hours: j
                                        });
                                        break;
                                    default:
                                        context.available_hours.push({
                                            day: section['available_hours'][runs[j].start].day
                                                  + ' - ' + section['available_hours'][runs[j].end].day,
                                            hours: j
                                        });
                                        break;
                                    }
                                    break;
                                }
                            }
                        }

                        context.fields = _prepSectionFields(section);

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
                        context.fields = _prepSectionFields(section);
                        tpl = Handlebars.compile($('#space-section').html());
                        html = tpl(context);
                    }

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

    var _prepSectionFields = function (section) {
        var fields = [],
            s, field;

        if (section.hasOwnProperty('fields')) {
            for (s in section.fields) {
                field = section.fields[s];
                fields.push({
                    name: field.name,
                    has_name: (field.name.length > 0),
                    value: (field.hasOwnProperty('value') && field.value.length > 0) ? field.value : 'No information'
                });
            }
        }

        return fields;
    };

    var _prettyHours = function (hours) {
        var t = hours.match(/^(([01]?\d)|2[0123]):([012345]\d)$/),
            h, m;

        if (t) {
            h = parseInt(t[1]);
            m = parseInt(t[3]);

            if (m == 0) {
                if (h == 0 || h == 23) {
                    return 'Midnight';
                } else if (h == 12) {
                    return 'Noon';
                }
            }

            return ((h > 12) ? (h - 12) : h)
                + ':' + ((m < 10) ? ('0' + m) : m)
                + ((h > 11) ? 'PM' : 'AM');
        }

        return hours;
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

});