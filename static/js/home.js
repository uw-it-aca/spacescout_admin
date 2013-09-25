$(document).ready(function() {

    /* home tabs */
    $('#myTab a').click(function (e) {
      e.preventDefault();
      $(this).tab('show');
      $($(this).attr('href')).children().trigger('exposed', ['Custom', 'Event']);
    });
    
    /* deal with tab exposure */
    $('#published').on('exposed', function (event) {
        loadPublishedSpaces();
    });

    $('#unpublished').on('exposed', function (event) {
        loadUnpublishedSpaces();
    });

    $('#incomplete').on('exposed', function (event) {
        loadIncompleteSpaces();
    });

    var spacesLoadingCue = function (selector) {
        var tpl_src = $('#list-item-loading').html();

        window.location.hash = selector.substr(1);
        $(selector).html(Handlebars.compile(tpl_src)());
    };

    var loadPublishedSpaces = function () {
        var selector = '#published';

        spacesLoadingCue(selector);

        $.ajax({
            url: 'api/v1/space/?published=1',
            dataType: 'json',
            error: ajaxSpaceError,
            success: function (data) {
                paintBuildlings(selector, data);
            }
        });
    };

    var loadUnpublishedSpaces = function () {
        var selector = '#unpublished';

        spacesLoadingCue(selector);

        $.ajax({
            url: 'api/v1/space/?complete=1&published=0',
            dataType: 'json',
            error: ajaxSpaceError,
            success: function (data) {
                paintBuildlings(selector, data);
            }
        });
    };

    var loadIncompleteSpaces = function () {
        var selector = '#incomplete';

        spacesLoadingCue(selector);

        $.ajax({
            url: 'api/v1/space/?complete=0&published=0',
            dataType: 'json',
            error: ajaxSpaceError,
            success: function (data) {
                var tpl_src, context, i, j;
                if (data.length) {
                    tpl_src = $('#incomplete-spaces').html();
                    context = {
                        spaces: []
                    };

                    $.each(data, function (i) {
                        var unfinished = [];
                        
                        for (j in data[i].missing_sections) {
                            unfinished.push({
                                id: data[i].id,
                                element: gettext(data[i].missing_sections[j].element),
                                section: data[i].missing_sections[j].section
                            });
                        }

                        context.spaces.push({
                            id: data[i].id,
                            name: data[i].name,
                            unfinished: unfinished,
                            last_modified: window.spacescout_admin.modifiedTime(new Date(data[i].last_modified)),
                            modified_by: (data[i].hasOwnProperty('modified_by') && data[i].modified_by && data[i].modified_by.length) ?
                                data[i].modified_by : gettext('unknown'),
                            manager: data[i].manager
                        });
                    });
                } else {
                    tpl_src = $('#no-spaces').html();
                    context = {};
                }

                $(selector).html(Handlebars.compile(tpl_src)(context));
            }
        });
    };

    var paintBuildlings = function (selector, data) {
        var tpl_src,
            context;

        if (data.length) {
            tpl_src = $('#building-groups').html();
            context = buildingGroupContext(data);
        } else {
            tpl_src = $('#no-spaces').html();
            context = {};
        }

        $(selector).html(Handlebars.compile(tpl_src)(context));
    };

    var buildingGroupContext = function (data) {
        var spaces = [],
            buildings = [],
            context = {
                buildings: []
            },
            i;

        $.each(data, function (i) {
            var space = data[i],
                building = space.location.building_name,
                space_data = {
                    id: space.id,
                    name: space.name,
                    description: space.description,
                    last_modified: window.spacescout_admin.modifiedTime(new Date(space.last_modified)),
                    modified_by: (space.hasOwnProperty('modified_by') && space.modified_by && space.modified_by.length) ? space.modified_by : gettext('unknown'),
                    manager: (space.manager.length > 0) ? space.manager : gettext('unknown'),
                    is_modified: space.is_modified,
                    is_published: space.is_published
                };

            if (building in spaces) {
                spaces[building].push(space_data);
            } else {
                buildings.push(building);
                spaces[building] = [space_data];
            }
        });

        for (i in buildings.sort()) {
            context.buildings.push({
                name: buildings[i],
                spaces: spaces[buildings[i]]
            });
        }

        return context;
    };

    var ajaxSpaceError = function (xhr) {
        var json;

        try {
            json = $.parseJSON(xhr.responseText);
            console.log('space search service error:' + json.error);
        } catch (e) {
            console.log('Unknown space service error');
        }
    };

    // initialize
    switch(decodeURIComponent(window.location.hash.substr(1))) {
    case 'unpublished' :
        $('a[href=#unpublished]').tab('show');
        loadUnpublishedSpaces();
        break;
    case 'incomplete' :
        $('a[href=#incomplete]').tab('show');
        loadIncompleteSpaces();
        break;
    default:
        loadPublishedSpaces();
        break;
    }

});