$(document).ready(function() {
    // prep for api post/put
    $.ajaxSetup({
        headers: { "X-CSRFToken": window.spacescout_admin.csrf_token }
    });

    (function () {
        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/space/' + window.spacescout_admin.space_id,
            dataType: 'json',
            success: function (data) {
                var next_action = function (key, value) {
                    var json_rep = {};

                    json_rep[key] = value;

                    $.ajax({
                        url: window.spacescout_admin.app_url_root + "api/v1/space/" + window.spacescout_admin.space_id + '/',
                        dataType: 'json',
                        contentType: "application/json",
                        data: JSON.stringify(json_rep),
                        type: "PUT",
                        success: function (data) {
                            window.location.href = window.spacescout_admin.app_url_root + '#published-spaces';
                        },
                        error: function (xhr, textStatus, errorThrown) {
                            alert('Error saving space: ' + textStatus + ' (' + errorThrown + ')');
                            console.log('textStatus: ' + textStatus + ' thrown: ' + errorThrown);
                        }
                    });
                };

                showSpaceDetails(data);

                $('.publish-button').click(function (event) {
                    $(event.target).unbind('click');
                    next_action('is_published', true);
                });
                /*
                $('.unpublish-button').click(function (event) {
                    $(event.target).unbind('click');
                    next_action('is_published', false);
                });
                */
                $('.submit-button').click(function (event) {
                    $(event.target).unbind('click');
                    next_action('is_pending_publication', true);
                });
            },
            error: function (xhr, textStatus, errorThrown) {
                var json;

                try {
                    json = $.parseJSON(xhr.responseText);
                    alert('Unable to load space:' + json.error);
                } catch (e) {
                    alert('Unable to load space: ' + xhr.responseText);
                }

                window.location.href = window.spacescout_admin.app_url_root;
            }
        });
    }());

    var showSpaceDetails = function (details) {
        var tpl, context, section, html, i, incomplete;

        $('.space-content-loading').hide();
        html = $(Handlebars.compile($('#space-details').html())({ name: details.name }));
        $('.space-content-loading').siblings(':last').after(html);

        for (i = 0; i < details.sections.length; i += 1) {
            section = details.sections[i];
            context = {
                section: gettext(section.section),
                edit_url: window.spacescout_admin.app_url_root + 'edit/' + window.spacescout_admin.space_id
                    + '/#' + encodeURIComponent(section.section)
            };

            switch (section.section) {
            case 'hours_access':
                context['available_hours'] = window.spacescout_admin.businessHours(section['available_hours']);
                if (!context['available_hours'].length) {
                    context.is_missing = true;
                }

                context.fields = prepSectionFields(section.fields);
                html = $(Handlebars.compile($('#space-section-hours').html())(context));
                break;
            case 'images':
                context['images'] = section['images'];
                if (context['images'].length) {
                    context['images'][0]['active'] = 'active';
                    context['images'][0]['description'] = gettext('defaultimage');
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

            if (section.section == 'images' && context['images'].length < 2) {
                $('#image-carousel .carousel-control').hide();
                $('#image-carousel .carousel-indicators').hide();
            }
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
            is_modified: details.is_modified,
            is_published: details.is_published,
            is_pending_publication: details.is_pending_publication,
            modified_by: (details.modified_by.length) ? details.modified_by : gettext('unknown'),
            last_modified: window.spacescout_admin.modifiedTime(new Date(details.last_modified))
        }));

        $('.space-content-loading').siblings(':last').after(html);
    };

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

    var modifiedTime = function (date) {
        var month = date.getMonth() + 1,
            hours = date.getHours(),
            late = (hours > 12),
            pm = gettext(late ? 'pm' : 'am'),
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
        var v,
            quote = true;

        if (f.hasOwnProperty('value') && typeof f.value === 'object') {
            v = window.spacescout_admin.getFieldValue(f.value);

            if (f.value.hasOwnProperty('map') && f.value.map.hasOwnProperty(v)) {
                v = gettext(f.value.map[v]);
            }

            if (((typeof v != 'string') || v.length > 0) && f.value.hasOwnProperty('format')) {
                v = f.value.format.replace('\{0\}', v);
                quote = false;
            }

            if (v.length) {
                return quote ? $('<div />').text(v).html() : v;
            }
        }

        return gettext('noinfo');
    };

});
