from django.core.urlresolvers import get_callable

from landlord import landlord, residence, DEFAULT_TENANT_KEY
from landlord.exceptions import TenantNotFound
from landlord.conf import settings

import threading


class LandlordMiddleware(object):
    def __init__(self):
        self.identifier = get_callable(settings.LANDLORD_IDENTIFIER_HANDLER)
        handler = settings.LANDLORD_TENANT_NOT_FOUND_HANDLER
        self.tenant_not_found_handler = get_callable(handler) if handler else None

    def process_request(self, request):
        credentials = self.identifier(request=request)

        if not credentials:
            request.tenant = None
            return None
            
        tenant = residence.find(**credentials)

        if tenant is None:
            raise TenantNotFound()

        landlord.push(tenant)
        request.tenant = tenant

    def process_response(self, request, response):
        tenant = getattr(request, DEFAULT_TENANT_KEY, None)
        if tenant:
            landlord.pop()
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, TenantNotFound):
            if self.tenant_not_found_handler:
                self.tenant_not_found_handler(request, exception)


# from django.db import transaction
# from django.middleware import TransactionMiddleware as DjangoTransactionMiddleware

# class TransactionMiddleware(DjangoTransactionMiddleware):
#     def process_request(self, request):
#         tenant = getattr(request, DEFAULT_TENANT_KEY, None)
#         if tenant:
#             transaction.enter_transaction_management(using=tenant)
#             transaction.managed(True, using=tenant)
#         return super(TransactionMiddleware, self).process_request(request)

#     def process_exception(self, request, exception):
#         tenant = getattr(request, DEFAULT_TENANT_KEY, None)
#         if tenant:
#             if transaction.is_dirty(using=tenant):
#                 transaction.rollback(using=tenant)
#             transaction.leave_transaction_management(using=tenant)
#         return super(TransactionMiddleware, self).process_exception(request, exception)

#     def process_response(self, request, response):
#         tenant = getattr(request, DEFAULT_TENANT_KEY, None)
#         if tenant:
#             if transaction.is_managed(using=tenant):
#                 if transaction.is_dirty(using=tenant):
#                     transaction.commit(using=tenant)
#                 transaction.leave_transaction_management(using=tenant)
#             return response
#         return super(TransactionMiddleware, self).process_response(request, response)
