from landlord.conf import settings


class ModelBackend(object):
    supports_tenant_creation = True

    tenant_model = None
    using_db = None

    def __init__(self, tenant_model=settings.LANDLORD_RESIDENCE_DEFAULT_BACKEND_MODEL, db=settings.LANDLORD_RESIDENCE_DEFAULT_BACKEND_DATABASE):
        self.loaded = False
        self.tenant_model = tenant_model
        self.using_db = db

        try:
            self.load()
        except:
            pass

    def load(self):
        #Taken and adapted from User.get_profile()
        from django.db.models import get_model
        try:
            app_label, model_name = self.tenant_model.split('.')
        except ValueError:
            raise Exception(
                'app_label and model_name should be separated by a dot in the LANDLORD_RESIDENCE_DEFAULT_BACKEND_MODEL setting'
            )

        model = get_model(app_label, model_name)
        if model is None:
            raise Exception('Could not load Tenant model')
        self.tenant_class = model
        self.loaded = True
        
    def create(self, name=None):    #make credentials to fit landlord.Tenant fields
        if not self.loaded:
            self.load()
        Tenant = self.tenant_class
        return Tenant.objects.using(self.using_db).create(name=name)

    def get(self, name=None):
        if not self.loaded:
            self.load()
        Tenant = self.tenant_class
        return Tenant.objects.using(self.using_db).get(name=name)