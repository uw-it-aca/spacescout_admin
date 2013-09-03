$(document).ready(function() {
    
    // hide the address bar... TODO: use the actual hide-address-bar.js script instead    
    window.scrollTo(0, 1);
        
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
            i, node, section = null;

        $('#space-name').html(space.name);

        for (i = 0; i < space.sections.length; i += 1) {
            if (hash == space.sections[i].section) {
                section = space.sections[i];
                break;
            }
        }

        if (!section) {
            $('#space-editor').html(Handlebars.compile($('#no-section').html())({}));
            return;
        }

        switch(hash) {
        case 'basic' :
            $('#space-editor').html(editBasicInfo(space));
            $('#input-space-name').keyup(function (e) {
                $('#space-name').html($(e.target).val());
            });

            break;
        case 'hours' :
            $('#space-editor').html(editHoursInfo(space));

            // DESKTOP: make the multi-day selector usable
            $('.selectpicker').selectpicker();
            
            // MOBILE: handle multi-day selection and display
            $('.day-select').change(function(){
                var selected = $(this).val();

                var list = $.map(selected, function(value) {
                    return(value);
                });
                
                $(this).siblings(".show-days").html(list.join(", "));
            });

            break;
        case 'images' :
            $('#space-editor').html(editImageInfo(section));
            break;
        default:
            $('#space-editor').append(editSectionInfo(section));
            break;
        }
    };

    var editBasicInfo = function (space) {
        var schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-basic').html()),
            context = {
                name: space.name,
                manager: space.manager,
                types: [],
                editors: space.editors.join(', ')
            },
            i, j, checked;

        for (i = 0; i < schema.type.length; i += 1) {
            checked = '';

            for (j = 0; j < space.type.length; j += 1) {
                if (space.type[j] == schema.type[i]) {
                    checked = 'checked';
                    break;
                }
            }

            context.types.push({
                name: gettext(schema.type[i]),
                value: 'schema.type[i]',
                checked: checked
            });
        }

        return tpl(context);
    };

    var editHoursInfo = function (space) {
        var schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-hours').html());

        return tpl({});
    };

    var editImageInfo = function (section) {
        var schema = window.spacescout_admin.spot_schema,
            tpl = Handlebars.compile($('#space-edit-images').html()),
            context = {};

        context['thumbnails'] = section['thumbnails'];
        if (context['thumbnails'].length) {
            context['thumbnails'][0]['active'] = 'active';
        }

        return tpl(context);
    };

    var editSectionInfo = function (space) {
        var schema = window.spacescout_admin.spot_schema,
            field, section, i, tpl;

        tpl = Handlebars.compile($('#editor-container').html());
        section = $(tpl({section: space.section}));

        for (i = 0; i < space.fields.length; i += 1) {
            field = space.fields[i];

            switch (typeof field.key) {
            case 'string':
                appendFieldValue(field, section);
                break;
            case 'object':
                if ($.isArray(field.key)) {
                    appendFieldList(field, section);
                }
                break;
            default:
                break;
            }
        }

        return section;
    };

    var appendFieldValue = function (field, section) {
        var tpl, vartype, data, i, node;

        // fields we know about
        switch (field.key) {
        case 'location.building_name':
            tpl = Handlebars.compile($('#space-edit-select').html());
            node = $(tpl({
                name: field.name,
                options: []
            }));

            section.append(node);

            $.ajax({
                url: '/api/v1/buildings/',
                dataType: 'json',
                success: function (data) {
                    var select = node.next('select'),
                        building = field.value,
                        option;

                    if (typeof data === 'object' && $.isArray(data)) {
                        for (i = 0; i < data.length; i += 1) {
                            option = $('<option></option>').val(i).html(data[i]);

                            if (building == data[i]) {
                                option.attr('selected', 'selected');
                            }

                            select.append(option);
                        }
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    XHRError(xhr);
                }
            });
            break;
        default:
            vartype = schemaVal(field.key);
            switch (typeof vartype) {
            case 'string':
                switch (vartype.toLowerCase()) {
                case 'unicode':
                    tpl = Handlebars.compile($('#space-edit-input').html());
                    section.append(tpl({
                        name: field.name,
                        help: (field.hasOwnProperty('help')) ? gettext(field.help) : '',
                        inputs: [{ value: field.value ? field.value : '' }]
                    }));
                    break;
                default:
                    break;
                }
                break;
            case 'object':
                if ($.isArray(vartype)) {
                    data = [];
                    for (i = 0; i < vartype.length; i += 1) {
                        data.push({
                            name: gettext(vartype[i]),
                            value: vartype[i]
                        });
                    }

                    tpl = Handlebars.compile($('#space-edit-select').html());
                    section.append(tpl({
                        name: field.name,
                        options: data
                    }));
                }
                break;
            default:
                break;
            }
        }
    };

    var appendFieldList = function(field, section) {
        var tpl, i, vartype, inputs = [];

        for (i = 0; i < field.key.length; i += 1) {
            
            vartype = schemaVal(field.key[i]);
            if (typeof vartype === 'string'
                && (vartype == 'unicode'
                    || vartype == 'decimal')) {
                inputs.push( field.value[i] );
            }
        }

        tpl = Handlebars.compile($('#space-edit-input').html());
        section.append(tpl({
            name: field.name,
            help: (field.hasOwnProperty('help')) ? gettext(field.help) : '',
            inputs: [{ value: inputs.join(', ') }]
        }));
    };

    var schemaVal = function (key) {
        var schema = window.spacescout_admin.spot_schema,
            keys = key.split('.'),
            val = null,
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

});