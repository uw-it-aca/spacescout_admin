$(document).ready(function() {

    /* home tabs */
    $('#myTab a').click(function (e) {
      e.preventDefault();
      $(this).tab('show');
      $($(this).attr('href')).children().trigger('exposed', ['Custom', 'Event']);
    });
    
    /* deal with tab exposure */
    $('#published').on('exposed', function (event) {
        loadPublishedSpots();
        loadUnpublishedSpots();
        loadIncompleteSpots();
    });

    $('#unpublished').on('exposed', function (event) {
        loadUnpublishedSpots();
    });

    $('#incomplete').on('exposed', function (event) {
        loadIncompleteSpots();
    });

    var spotsLoadingCue = function (selector) {
        var tpl_src = $('#list-item-loading').html();

        $(selector).html(Handlebars.compile(tpl_src)());
    };

    var loadPublishedSpots = function () {
        var selector = '#published';

        spotsLoadingCue(selector);

        $.ajax({
            url: 'api/v1/spot/',
            dataType: 'json',
            success: function (data) {
                var tpl_src,
                    context;

                if (data.length) {
                    tpl_src = $('#building-groups').html();
                    context = buildingGroupContext(data);
                } else {
                    tpl_src = $('#no-spots').html();
                    context = {};
                }

                $(selector).html(Handlebars.compile(tpl_src)(context));
            },
            error: function (xhr, textStatus, errorThrown) {
                var json;

                try {
                    json = $.parseJSON(xhr.responseText);
                    console.log('spot search service error:' + json.error);
                } catch (e) {
                    console.log('Unknown spot service error');
                }
            }
        });
    };

    var loadUnpublishedSpots = function () {
        var selector = '#unpublished';

        spotsLoadingCue(selector);

        // REMOVE BEFORE FLIGHT
        var data = [
            {
                id: '11111',
                name: 'Space 1',
                last_modified: '',
                manager: 'Donald Duck',
                location: { building_name: 'Building A'},
                last_modified: '2013-03-19T20:47:19+00:00',
                extended_info: { location_description: 'Funky Space A-1' }
            },
            {
                id: '3333',
                name: 'Space A',
                last_modified: '',
                manager: 'Mickey Mouse',
                location: { building_name: 'Building B'},
                last_modified: '2013-03-19T20:37:19+00:00',
                extended_info: { location_description: 'Funky Space B-1' }
            },
            {
                id: '22222',
                name: 'Space 2',
                last_modified: '',
                manager: 'Donald Duck',
                location: { building_name: 'Building A'},
                last_modified: '2013-03-19T20:27:19+00:00',
                extended_info: { location_description: 'Funky Space A-2' }
            }
        ];

        
        if (Math.floor(Math.random() * (100) + 1) > 80) {
            data = [];
        }

        setTimeout( function () {
        var tpl_src,
            context;

        if (data.length) {
            tpl_src = $('#building-groups').html();
            context = buildingGroupContext(data);
        } else {
            tpl_src = $('#no-spots').html();
            context = {};
        }

        $(selector).html(Handlebars.compile(tpl_src)(context));
        }, Math.floor(Math.random() * (2250 - 250 + 1) + 250));
    };

    var loadIncompleteSpots = function () {
        var selector = '#incomplete';

        spotsLoadingCue(selector);

        // REMOVE BEFORE FLIGHT
        var data = [
            {
                id: 111,
                name: 'Space A',
                last_modified: '2013-03-19T20:07:19+00:00',
                manager: 'mikes',
                todo: ['Description',
                       'Photo',
                       'Hours']
            },
            {
                id: 222,
                name: 'Space B',
                last_modified: '2013-03-19T20:07:19+00:00',
                manager: 'mikes',
                todo: ['Photo',
                       'Hours',
                       'Resources',
                       'Type']
            },
            {
                id: 3333,
                name: 'Spacey Space with a really long name for you to test',
                last_modified: '2013-03-19T20:07:19+00:00',
                manager: 'mikes',
                todo: ['Description', 'Food/Coffee']
            }
        ];

        setTimeout( function () {
        var tpl, context, i, j;

        if (data.length) {
            tpl = Handlebars.compile($('#incomplete-spots').html());
            context = {
                spots: []
            };

            $.each(data, function (i) {
                var unfinished = [];
 
                for (j in data[i].todo) {
                    unfinished.push({
                        element: data[i].todo[j]
                    });
                }

                context.spots.push({
                    id: data[i].id,
                    name: data[i].name,
                    unfinished: unfinished,
                    last_modified: window.spacescout_admin.modifiedTime(new Date(data[i].last_modified)),
                    modified_by: (data[i].hasOwnProperty('modified_by') && data[i].modified_by.length) ?
                        data[i].modified_by : gettext('unknown'),
                    manager: data[i].manager
                });
            });
       } else {
           tpl = Handlebars.compile($('#no-spots').html());
           context = {};
       }
        
        $(selector).html(tpl(context));
        }, Math.floor(Math.random() * (2250 - 250 + 1) + 250));
    };

    var buildingGroupContext = function (data) {
        var spots = [],
            buildings = [],
            context = {
                buildings: []
            },
            i;

        $.each(data, function (i) {
            var spot = data[i],
                building = spot.location.building_name,
                spot_data = {
                    id: spot.id,
                    name: spot.name,
                    description: spot.extended_info.hasOwnProperty('location_description') ? spot.extended_info.location_description : '',
                    last_modified: window.spacescout_admin.modifiedTime(new Date(spot.last_modified)),
                    modified_by: (spot.hasOwnProperty('modified_by') && spot.modified_by.length) ? spot.modified_by : gettext('unknown'),
                    manager: (spot.manager.length > 0) ? spot.manager : gettext('unknown'),
                    is_modified: true
                };

            if (building in spots) {
                spots[building].push(spot_data);
            } else {
                buildings.push(building);
                spots[building] = [spot_data];
            }
        });

        for (i in buildings.sort()) {
            context.buildings.push({
                name: buildings[i],
                spots: spots[buildings[i]]
            });
        }

        return context;
    };

    // initialize
    loadPublishedSpots();

});