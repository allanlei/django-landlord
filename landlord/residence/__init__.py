from landlord.conf import settings
from landlord.signals import tenant_created, residence_init
from landlord.residence.utils import load_backend


class Residence(object):
    '''
    Persistance: Non-persistent
    Thread-safety: not required
    Implement via ResidenceBackends or TenantBackends, similar to AUTHENTICATION_BACKENDS
    Also similar to AuthenticationBackends, adapt Permissions system to DatabaseSettings

    Init with a storage area to search for Tenants
    '''
    def __init__(self, backend=settings.LANDLORD_RESIDENCE_DEFAULT_BACKEND):
        self.backend_class = load_backend(backend)
        residence_init.send(sender=self)
    
    def create(self, **credentials):
        if not self.backend_class.supports_tenant_creation:
            raise Exception('Residence backend specified does not support Tenant creations.')

        backend = self.backend_class()
        tenant = backend.create(**credentials)

        tenant_created.send(sender=self, instance=tenant, created=True)
        return tenant
        

    def get(self, **credentials):
        tenant = self.find(**credentials)
        if tenant:
            return tenant
        raise TenantNotFound()

    def find(self, **credentials):
        backend = self.backend_class()

        try:
            tenant = backend.get(**credentials)
        except TypeError:
            pass

        if tenant:
            tenant.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
        return tenant

    # def __getitem__(self, key):
        # pass

    # def __iter__(self):
        # print 'OMMMMMMGG'
        # return None
        # return list of all Tenants