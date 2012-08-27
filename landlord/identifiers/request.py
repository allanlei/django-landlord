from landlord import DEFAULT_TENANT_KEY
from landlord.exceptions import TenantNotFound


def GET_param(request, param=DEFAULT_TENANT_KEY):
    if param in request.GET and request.GET[param]:
        return {
            'name': request.GET[param],
        }