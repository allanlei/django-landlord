class LandlordRouter(object):
    def update_ignored_models(self):
        from django.db.models.loading import get_models, get_model, get_app
        from landlord.conf import settings
        ignored_apps = tuple(settings.LANDLORD_ROUTER_IGNORED_APPS)
        ignored_models = settings.LANDLORD_ROUTER_IGNORED_MODELS

        models = set()
        for app in ignored_apps:
            models.update(set(get_models(get_app(app))))

        for model in ignored_models:
            models.add(get_model(*model.split('.')))

        self.ignored_models = models

    def db_for_read(self, model, **hints):
        if not getattr(self, 'ignored_models', None):
            self.update_ignored_models()

        if model in self.ignored_models:
            return None

        tenant = hints.get('tenant', None)# or landlord.get_current_tenant()
        if tenant:
            return str(tenant)

    def db_for_write(self, model, **hints):
        if not getattr(self, 'ignored_models', None):
            self.update_ignored_models()

        if model in self.ignored_models:
            return None

        tenant = hints.get('tenant', None)  # or landlord.get_current_tenant()
        if tenant:
            return str(tenant)
        
    # def allow_relation(self, obj1, obj2, **hints):
        # settings.LANDLORD_ROUTER_RELATION_IGNORE
        # return landlord.current_tenant
        # print 'allow_relation: ', obj1, obj2, hints

    def allow_syncdb(self, db, model):
        if not getattr(self, 'ignored_models', None):
            self.update_ignored_models()

        if model in self.ignored_models:
            return None

        # settings.LANDLORD_ROUTER_SYNCDB_IGNORE
        # return landlord.current_tenant
        # print 'allow_syncdb: ', db, model