$(document).ready(function() {

    // prep for api delete
    $.ajaxSetup({
        headers: { "X-CSRFToken": window.spacescout_admin.csrf_token }
    });

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
                var tpl_src, context, i;

                if (data.length) {
                    tpl_src = $('#incomplete-spaces').html();
                    context = {
                        spaces: []
                    };

                    $.each(data, function () {
                        var unfinished = [];

                        for (i in this.missing_fields) {
                            unfinished.push({
                                id: this.id,
                                field: gettext(this.missing_fields[i].field),
                                section: this.missing_fields[i].section
                            });
                        }

                        context.spaces.push({
                            id: this.id,
                            name: this.name,
                            unfinished: unfinished,
                            last_modified: window.spacescout_admin.modifiedTime(new Date(this.last_modified)),
                            modified_by: (this.hasOwnProperty('modified_by') && this.modified_by && this.modified_by.length) ?
                                this.modified_by : gettext('unknown'),
                            manager: this.manager
                        });
                    });
                } else {
                    tpl_src = $('#no-spaces').html();
                    context = {};
                }

                $(selector).html(Handlebars.compile(tpl_src)(context));

                $('.delete-space').click(function (e) {
                    var t = $(e.target),
                        id = t.prop('id').match(/space_([0-9]+)/)[1],
                        name = t.prev().find('span').text();

                    if (confirm('Really delete space "' + name + '"?')) {
                        $.ajax({
                            url: window.spacescout_admin.app_url_root + 'api/v1/space/' + id + '/',
                            type: 'DELETE',
                            success: function (data) {
                                if (t.parent().parent().children().length > 1) {
                                    t.parent().slideUp('fast');
                                } else {
                                    window.location.reload();
                                }
                            },
                            error: ajaxSpaceError
                        });
                    }
                });
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

        $.each(data, function () {
            var group = this.group,
                space_data = {
                    id: this.id,
                    name: this.name,
                    description: this.description,
                    last_modified: window.spacescout_admin.modifiedTime(new Date(this.last_modified)),
                    modified_by: (this.hasOwnProperty('modified_by') && this.modified_by && this.modified_by.length) ? this.modified_by : gettext('unknown'),
                    manager: (this.manager.length > 0) ? this.manager : gettext('unknown'),
                    is_modified: this.is_modified,
                    is_pending: this.is_pending,
                    is_published: this.is_published,
                    is_pending_publication: this.is_pending_publication
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