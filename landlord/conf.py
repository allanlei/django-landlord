from django.conf import settings
from appconf import AppConf


class LandlordAppConf(AppConf):
    #Landlord
    DEFAULT_INSTANCES = True
    IDENTIFIER_HANDLER = 'landlord.identifiers.request.GET_param'
    ROUTER_IGNORED_APPS = (
        'landlord',
    )
    ROUTER_IGNORED_MODELS = ()
    ROUTER_ENABLE_HINTS = True

    ROUTING_READ_HANDLER = ''
    ROUTING_WRITE_HANDLER = ''
    ROUTING_RELATION_HANDLER = ''
    ROUTING_SYNCDB_HANDLER = ''

    #Residence
    RESIDENCE_DEFAULT_BACKEND = 'landlord.residence.backends.ModelBackend'
    RESIDENCE_DEFAULT_BACKEND_MODEL = 'landlord.Tenant'
    RESIDENCE_DEFAULT_BACKEND_DATABASE = 'default'
    DEFAULT_RESIDENCE_ALIAS = 'default'
    RESIDENCE = {
        'default': {
            'BACKEND': 'landlord.residence.backend.ModelBackend',
            'OPTIONS': {
                'db': 'default',
                'model': 'landlord.Tenant',
            }
        }
    }

    #Tenant
    TENANT_NOT_FOUND_HANDLER = None
    REQUEST_MAPPER = None