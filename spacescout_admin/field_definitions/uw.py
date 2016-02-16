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
            'name': 'Space Type',
            'required': True,
            'help': {
                'text': 'space_type_help'
            },
            'value': {
                'key': 'type',
                'edit': {
                    'multi_select': True,
                    'limit': 2
                }
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
        }
    ]

def space_definitions():
    return  [
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
                    'name': 'Space Type',
                    'required': True,
                    'help': {
                        'text': 'space_type_help'
                    },
                    'value': {
                        'key': 'type',
                        'edit': {
                            'multi_select': True,
                            'limit': 2
                        }
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
                }
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
                    'name': 'Building',
                    'required': True,
                    'value': {
                        'key': 'location.building_name',
                        'edit': {
                            'dependency' : {
                                'key': 'extended_info.campus'
                            }
                        }
                    }
                },
                {
                    'name': 'location_alias',
                    'help': {
                        'text': 'location_alias_help',
                        'expanded': { 
                            'text': 'location_alias_more_help', 
                            'link': 'location_alias_link'
                        }
                    },
                    'value': {
                        'key': 'extended_info.location_alias'
                    }
                },
    
                {
                    'name': 'Floor',
                    'required': True,
                    'help': {
                        'text': 'floor_help'
                    },
                    'value': {
                        'key': 'location.floor'
                    }
                },
                {
                    'name': 'room_number',
                    'help': {
                        'text': 'room_number_help'
                    },
                    'value': {
                        'key': 'location.room_number'
                    }
                },
                {
                    'name': 'description',
                    'help': {
                        'text': 'description_help',
                        'expanded': {
                            'text': 'description_more_help',
                            'link': 'description_link'
                        }
                    },
                    'required': True,
                    'value': {
                        'key': 'extended_info.location_description'
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
                {
                    'name': 'cafe_hours',
                    'help': {
                        'text': 'cafe_hours_help',
                        'expanded': {
                            'text': 'cafe_hours_more_help',
                            'link': 'cafe_hours_link'
                        }
                    },
                    'value': {
                        'key': 'extended_info.cafe_hours',
                        'edit': {
                            'tag': 'textarea'
                        }
                    }
                },
                {
                    'name': 'access_notes',
                    'help': {
                        'text': 'access_notes_help',
                        'expanded': {
                            'text': 'access_notes_more_help',
                            'link': 'See Examples'
                        }
                    },
                    'value': {
                        'key': 'extended_info.access_notes',
                        'edit': {
                            'tag': 'textarea'
                        }
                    }
                },
                {
                    'name': 'Reservability',
                    'help': {
                        'text': 'reservability_help'
                    },
                    'value': {
                        'key': 'extended_info.reservable',
                        'edit': {
                            'default': None,
                            'requires': 'extended_info.reservation_notes'
                        },
                        'map': [
                            {
                                'value': '',
                                'display': 'cannotreserve'
                            },
                            {
                                'value': 'true',
                                'display': 'canreserve'
                            },
                            {
                                'value': 'reservations',
                                'display': 'mustreserve'
                            }
                        ],
                        'format': '<em>{0}</em>'
                    }
                },
                {
                    'name': 'Reservation Notes',
                    'help': {
                        'text': 'reservation_notes_help',
                        'expanded': {
                            'text': 'reservation_notes_more_help',
                            'link': 'See Examples'
                        }
                    },
                    'value': {
                        'key': 'extended_info.reservation_notes',
                        'edit': {
                            'tag': 'textarea'
                        }
                    }
                }
            ]
        },
        {
            'section': 'resources',
            'fields': [
                {
                    'name': 'Resources',
                    "help": {
                        'text': "resources_help"
                    },
                    'value': [
                        {
                            'key': 'extended_info.has_outlets'
                        },
                        {
                            'key': 'extended_info.has_projector'
                        },
                        {
                            'key': 'extended_info.has_displays'
                        },
                        {
                            'key': 'extended_info.has_whiteboards'
                        },
                        {
                            'key': 'extended_info.has_printing'
                        },
                        {
                            'key': 'extended_info.has_scanner'
                        },
                        {
                            'key': 'extended_info.has_computers'
                        }
                    ]
                },
                {
                    'name': 'Capacity',
                    'help': {
                        'text': 'capacity_help'
                    },
                    'value': {
                        'key': 'capacity',
                        'format': 'Seats {0}'
                    }
                },
                {
                    'name': 'Lighting',
                    'value': {
                        'key': 'extended_info.has_natural_light'
                    }
                },
                {
                    'name': 'noise_level',
                    'help': {
                        'text': 'noise_level_help',
                        'expanded': {
                            'text': 'noise_level_more_help',
                            'link': 'See Examples'
                        }
                    },
                    'value': {
                        'key': 'extended_info.noise_level'
                    }
                },
                {
                    'name': 'food_coffee',
                    'help': {
                        'text': 'food_coffee_help'
                    },
                    'value': {
                        'key': 'extended_info.food_nearby',
                        'edit' : {
                            'default': None
                        },
                        'map': [
                            {
                                'value': '',
                                'display': 'unset'
                            },
                            {
                                'value': 'space',
                                'display': 'space'
                            },
                            {
                                'value': 'building',
                                'display': 'building'
                            },
                            {
                                'value': 'neighboring',
                                'display': 'neighboring'
                            }
                        ]
                    }
                }
            ]
        },
        {
            # images managed dinternally
            'section': 'images'
        }
    ]


