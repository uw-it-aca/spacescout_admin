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

        window.location.hash = selector.substr(1) + '-spaces';
        $(selector).html(Handlebars.compile(tpl_src)());
    };

    var loadPublishedSpaces = function () {
        var selector = '#published';

        spacesLoadingCue(selector);

        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/space/?published=1',
            dataType: 'json',
            error: ajaxSpaceError,
            success: function (data) {
                paintGroupings(selector, data);
            }
        });
    };

    var loadUnpublishedSpaces = function () {
        var selector = '#unpublished';

        spacesLoadingCue(selector);

        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/space/?complete=1&published=0',
            dataType: 'json',
            error: ajaxSpaceError,
            success: function (data) {
                paintGroupings(selector, data);
            }
        });
    };

    var loadIncompleteSpaces = function () {
        var selector = '#incomplete';

        spacesLoadingCue(selector);

        $.ajax({
            url: window.spacescout_admin.app_url_root + 'api/v1/space/?complete=0&published=0',
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

                        for (j in data[i].missing_fields) {
                            unfinished.push({
                                id: data[i].id,
                                field: gettext(data[i].missing_fields[j].field),
                                section: data[i].missing_fields[j].section
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

    var paintGroupings = function (selector, data) {
        var tpl_src,
            context;

        if (data.length) {
            tpl_src = $('#grouping-groups').html();
            context = groupContext(data);
        } else {
            tpl_src = $('#no-spaces').html();
            context = {};
        }

        $(selector).html(Handlebars.compile(tpl_src)(context));
    };

    var groupContext = function (data) {
        var spaces = [],
            groupings = [],
            context = {
                groupings: []
            },
            i;

        $.each(data, function (i) {
            var space = data[i],
                group = space.group,
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

            if (group in spaces) {
                spaces[group].push(space_data);
            } else {
                groupings.push(group);
                spaces[group] = [space_data];
            }
        });

        for (i in groupings.sort()) {
            context.groupings.push({
                name: groupings[i],
                spaces: spaces[groupings[i]]
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
    case 'unpublished-spaces' :
        $('a[href=#unpublished]').tab('show');
        loadUnpublishedSpaces();
        break;
    case 'incomplete-spaces' :
        $('a[href=#incomplete]').tab('show');
        loadIncompleteSpaces();
        break;
    default:
        loadPublishedSpaces();
        break;
    }

});