def creation_fields():
    return [
        {
            'name': 'Space Name',
            'required': True,
            'value': {
                'key': 'name'
            }
        },
        {
            'name': 'Owner',
            'required': True,
            'value': {
                'key': 'manager',
                'edit': {
                    'default': '{{ username }}'
                    }
                }
        },
    ]


def space_definitions():
    return [
        {
            'section': 'basic',
            'fields': [
                {
                    'name': 'Space Name',
                    'help': {
                        'text': 'space_name_help'
                    },
                    'required': True,
                    'value': {
                        'key': 'name'
                    }
                },
                {
                    'name': 'Owner',
                    'required': True,
                    'help': {
                        'text': 'owner_help'
                    },
                    'value': {
                        'key': 'manager'
                    }
                },
                {
                    'name': 'Editors',
                    'help': {
                        'text': 'editors_help'
                    },
                    'value': {
                        'key': 'editors'
                    }
                },
            ]
        },
        {
            'section': 'location',
            'fields': [
                {
                    'name': 'Campus',
                    'value': {
                        'key': 'extended_info.campus',
                        'edit': {
                            'tag': 'select'
                         }
                    }
                },
                {
                    'name': 'latlong',
                    'required': True,
                    'help': {
                        'text': 'latlong_help',
                        'expanded': {
                            'text': 'latlong_more_help',
                            'link': 'latlong_link'
                        }
                    },
                    'value': [
                        {
                            'key': 'location.latitude'
                        },
                        {
                            'key': 'location.longitude'
                        }
                    ]
                }
            ]
        },
        {
            # hours field managed internally
            'section': 'hours_access',
            'fields': [
                {
                    'name': 'notes',
                    'help': {
                        'text': 'hours_notes_help'
                    },
                    'value': {
                        'key': 'extended_info.hours_notes',
                        'edit': {
                            'tag': 'textarea'
                        }
                    }
                },
            ]
        },
        {
            # images managed internally
            'section': 'images'
        },
    ]
