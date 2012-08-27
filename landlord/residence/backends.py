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