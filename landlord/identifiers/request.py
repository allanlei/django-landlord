from landlord.exceptions import TenantNotFound


def GET_param(request):
    return {
        'name': request.GET.get('tenant', None),
    }

def META_host(request):
    return {
        'name': request.META.get('HTTP_HOST', None),
    }