from landlord.conf import settings
from landlord.signals import tenant_precreate, tenant_created, residence_init
from landlord.residence.utils import load_backend


class BaseResidence(object):
    '''
    Persistance: Non-persistent
    Thread-safety: not required
    Implement via ResidenceBackends or TenantBackends, similar to AUTHENTICATION_BACKENDS
    Also similar to AuthenticationBackends, adapt Permissions system to DatabaseSettings

    Init with a storage area to search for Tenants
    '''

    def __init__(self):
        residence_init.send(sender=self)

    def create(self, **kwargs):
        '''
        Creates a Tenant object
        kwargs: Tenant init options
        returns
        '''
        raise NotImplementedError()

    def query(self, **kwargs):
        '''
        returns list of all Tenants filtering by kwargs
        if kwargs is empty, returns all Tenants
        '''
        raise NotImplementedError()

    def get(self, **kwargs):
        '''
        returns exactly 1 Tenant object
        raise multiple if error
        '''
        query = self.query(**kwargs)
        if len(query) <= 0:
            raise Exception('')
        elif len(query) > 1:
            raise Exception('')
        return self.query(**kwargs)[0]

    def get_or_create(self, **kwargs):
        try:
            return self.get(**kwargs), False
        except:
            return self.create(**kwargs), True

    def __iter__(self):
        query = self.query()
        for tenant in query:
            yield tenant


class ModelResidence(object):
    def __init__(self, backend=settings.LANDLORD_RESIDENCE_DEFAULT_BACKEND, *args, **kwargs):
        self.__backend_class = backend
        super(ModelResidence, self).__init__(*args, **kwargs)
    
    @property
    def backend(self):
        if not getattr(self, '__backend', None):
             backend = load_backend(self.__backend_class)
             self.__backend = backend()
        return self.__backend

    def create(self, **credentials):
        # if not self.backend_class.supports_tenant_creation:
            # raise Exception('Residence backend specified does not support Tenant creations.')

        tenant_precreate.send(sender=self, credentials=credentials)
        tenant = self.backend.create(**credentials)

        tenant_created.send(sender=self, instance=tenant, created=True, backend=self.backend)
        return tenant

    def get(self, **credentials):
        tenant = self.backend.get(**credentials)
        # if tenant:
            # tenant.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
        return tenant

    def query(self, **credentials):
        tenant = None
        try:
            tenant = self.get(**credentials)
        except:
            pass
        return tenant

    find = query

    def get_or_create(self, **credentials):
        tenant, created = None, False
        return tenant, created

    # def __getitem__(self, key):
        # pass

    # def __repr__(self):
        # <landlord.residence.Residence object at 0x2e10110>
        # return 'Residence< '

    # def __len__(self):
        # print list(self)
        # return 0
        # return len(list(self))

    def __iter__(self):
        for tenant in self.backend:
            yield tenant



from landlord.conf import settings


class ModelBackend(object):
    supports_tenant_creation = True

    tenant_model = None
    using_db = None

    def __init__(self, model=settings.LANDLORD_RESIDENCE_DEFAULT_BACKEND_MODEL, db=settings.LANDLORD_RESIDENCE_DEFAULT_BACKEND_DATABASE):
        self.__tenant_model_class = model
        self.using_db = db

    @property
    def tenant_model(self):
        if not getattr(self, '__tenant_model', None):
            from django.db.models import get_model
            try:
                app_label, model_name = self.__tenant_model_class.split('.')
            except ValueError:
                raise Exception(
                    'app_label and model_name should be separated by a dot in the LANDLORD_RESIDENCE_DEFAULT_BACKEND_MODEL setting'
                )

            model = get_model(app_label, model_name)
            if model is None:
                raise Exception('Could not load Tenant model')
            self.__tenant_model = model
        return self.__tenant_model
        
    def create(self, name=None):    #make credentials to fit landlord.Tenant fields
        return self.tenant_model.objects.using(self.using_db).create(name=name)

    def get(self, name=None):
        return self.tenant_model.objects.using(self.using_db).get(name=name)

    def __iter__(self):
        for tenant in self.tenant_model.objects.all():
            yield tenant