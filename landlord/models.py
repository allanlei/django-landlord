from landlord import landlord
from conf import settings

if settings.LANDLORD_ENABLE_ROUTER_HINTS:
    from routers import enable_router_hints
    enable_router_hints()


class LandlordTrackingMixin(object):
    def __enter__(self):
        landlord.push(self)
    
    def __exit__(self, type, value, tb):
        landlord.pop()