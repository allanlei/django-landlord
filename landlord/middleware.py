from django.http import Http404
from django.core.urlresolvers import get_callable

from landlord import landlord
from landlord.conf import settings


class LandlordMiddleware(object):
    def __init__(self):
        self.identify = get_callable(settings.LANDLORD_REQUEST_IDENTIFIER)
        
        # handler = settings.LANDLORD_NAMESPACE_NOT_FOUND_HANDLER
        # self.namespace_not_found_handler = get_callable(handler) if handler else None

    def process_request(self, request):
        namespace = self.identify(request=request)

        if not namespace and settings.HTTP_404_ON_UNKNOWN_NAMESPACE:
            raise Http404()
            
        landlord.push(namspace)
        request.namespace = namespace

    def process_response(self, request, response):
        if hasattr(request, settings.LANDLORD_DEFAULT_NAMESPACE_KEY):
            namespace = getattr(request, settings.LANDLORD_DEFAULT_NAMESPACE_KEY)
            if namespace:
                landlord.pop()
        return response

    # def process_exception(self, request, exception):
    #     if isinstance(exception, TenantNotFound):
    #         if self.tenant_not_found_handler:
    #             self.tenant_not_found_handler(request, exception)