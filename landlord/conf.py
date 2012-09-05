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

    # ROUTING_READ_HANDLER = ''
    # ROUTING_WRITE_HANDLER = ''
    # ROUTING_RELATION_HANDLER = ''
    # ROUTING_SYNCDB_HANDLER = ''

    #Residence
    RESIDENCE_DEFAULT_BACKEND = 'landlord.residence.backends.ModelBackend'
    RESIDENCE_MODELBACKEND_MODEL = 'landlord.Tenant'
    RESIDENCE_DEFAULT_BACKEND_MODEL = RESIDENCE_MODELBACKEND_MODEL
    RESIDENCE_DEFAULT_BACKEND_DATABASE = 'default'

    #Tenant