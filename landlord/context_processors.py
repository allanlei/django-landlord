# from django.conf import settings
from landlord import residence


def landlord(request):
    return {
        # 'landlord': landlord,
        # 'residence': residence,
        'current_tenant': request.tenant,
        'tenants': list(residence),
    }