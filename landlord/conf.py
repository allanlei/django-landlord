from django.conf import settings
from appconf import AppConf


class LandlordAppConf(AppConf):
    DEFAULT_NAMESPACE_KEY = 'namespace'
    REQUEST_IDENTIFIER = 'landlord.identifiers.request_query_parameter'
    ENABLE_ROUTER_HINTS = True
    HTTP_404_ON_UNKNOWN_NAMESPACE = True