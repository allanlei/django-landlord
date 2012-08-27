from landlord.conf import settings

import os

def env_key(key=settings.LANDLORD_DEFAULT_TENANT_KEY.upper()):
    return os.environ.get(key, None)

def request_query_parameter(request, param=settings.LANDLORD_DEFAULT_TENANT_KEY):
    if param in request.GET and request.GET[param]:
        return {
            'name': request.GET[param],
        }