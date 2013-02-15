from django import template
register = template.Library()


@register.filter
def lookup(dictionary, key):
    """ returns the value of dictionary[key] in a template.
    """
    try:
        return dictionary[key]
    except KeyError:
        try:
            return dictionary['location'][key]
        except KeyError:
            try:
                return dictionary['extended_info'][key]
            except KeyError:
                return ''
    except Exception as e:
        return e.__class__()


@register.filter
def classname(obj):
    """ returns the classname of an object in a template.
    """
    return obj.__class__.__name__
