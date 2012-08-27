from django.db import models

from landlord.conf import settings

if settings.LANDLORD_ROUTER_ENABLE_HINTS:
    from landlord.hacks import add_tenant_to_router_hints
    add_tenant_to_router_hints()


class Tenant(models.Model):
    name = models.CharField(max_length=256, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __enter__(self):
        from landlord import landlord
        landlord.push(self)
    
    def __exit__(self, type, value, tb):
        from landlord import landlord
        landlord.pop()

    def __unicode__(self):
        return self.name