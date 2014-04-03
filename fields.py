from django.utils.importlib import import_module
from django.conf import settings

def space_creation_fields():
    module = _get_mod()
    return module.creation_fields()

def space_definitions():
    module = _get_mod()
    return module.space_definitions()


def _get_mod():
    module = getattr(settings, 'SS_ADMIN_FIELDS_MODULE', 'spacescout_admin.field_definitions.default')
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))

    return mod

