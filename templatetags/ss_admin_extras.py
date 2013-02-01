from django import template
register = template.Library()


@register.filter
def lookup(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        try:
            return dictionary['location'][key]
        except KeyError:
            try:
                return dictionary['extended_info'][key]
            except KeyError:
                return 'no value'
    except Exception as e:
        return e.__class__()


@register.filter
def classname(obj):
    return obj.__class__.__name__
