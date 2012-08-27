from django.core.urlresolvers import get_callable

from landlord import landlord, residence
from landlord.exceptions import TenantNotFound
from landlord.conf import settings

class LandlordMiddleware(object):
    def __init__(self):
        self.identifier = get_callable(settings.LANDLORD_IDENTIFIER_HANDLER)

    def process_request(self, request):
        credentials = self.identifier(request=request)
        tenant = residence.find(**credentials)

        if tenant is None:
            raise TenantNotFound()

        landlord.push(tenant)
        request.tenant = tenant

    def process_response(self, request, response):
        print 'pop(): ', landlord.pop()
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, TenantNotFound):
            return get_callable(settings.LANDLORD_TENANT_NOT_FOUND_HANDLER)(request)




# class TenantMiddleware(object):
#     def identify_tenant(self, request):
#         name = None
        
#         if name is None:
#             try:
#                 name = resolve(request.path).kwargs.get('tenant', None)
#             except:
#                 pass
#         if name is None:
#             name = request.GET.get('tenant', None)
#         return name
        
#     def process_request(self, request):
#         request.tenant = None
        
#         name = self.identify_tenant(request)
#         if name:
#             tenant = get_object_or_404(Tenant, name=name)
#             request.tenant = tenant
#             connect_tenant_provider(request, tenant.ident)
#         return None
        
#     def process_response(self, request, response):
#         disconnect_tenant_provider(request)
#         request.tenant = None
#         return response


# class TransactionMiddleware(object):
#     def get_tenant(self, request):
#         tenant = getattr(request, 'tenant', None)
#         if tenant:
#             return tenant.ident
        
#     def process_request(self, request):
#         """Enters transaction management"""
#         transaction.enter_transaction_management(using=self.get_tenant(request))
#         transaction.managed(True, using=self.get_tenant(request))

#     def process_exception(self, request, exception):
#         """Rolls back the database and leaves transaction management"""
#         if transaction.is_dirty(using=self.get_tenant(request)):
#             transaction.rollback(using=self.get_tenant(request))
#         transaction.leave_transaction_management(using=self.get_tenant(request))

#     def process_response(self, request, response):
#         """Commits and leaves transaction management."""
#         if transaction.is_managed(using=self.get_tenant(request)):
#             if transaction.is_dirty(using=self.get_tenant(request)):
#                 transaction.commit(using=self.get_tenant(request))
#             transaction.leave_transaction_management(using=self.get_tenant(request))
#         return response
