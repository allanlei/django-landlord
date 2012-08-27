from warnings import warn
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def load_backend(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing residence backend %s: "%s"' % (path, e))
    # except ValueError, e:
        # raise ImproperlyConfigured('Error importing residence backends. Is AUTHENTICATION_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" residence backend' % (module, attr))

    # if not hasattr(cls, 'supports_database'):
        # warn("Authentication backends without a `supports_inactive_user` attribute are deprecated. Please define it in %s." % cls,
             # DeprecationWarning)
        # cls.supports_inactive_user = False
    return cls