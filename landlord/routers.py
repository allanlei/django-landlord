# from landlord import landlord
# from landlord.conf import settings

# import logging
# logger = logging.getLogger(__name__)



# class LandlordRouter(object):
#     @property
#     def ignored_models(self):
#         if not getattr(self, '__ignored_models', None):
#             from django.db.models.loading import get_models, get_model, get_app
#             from landlord.conf import settings
#             models = set()

#             ignored_apps = tuple(settings.LANDLORD_ROUTER_IGNORED_APPS)
#             for app in ignored_apps:
#                 models.update(set(get_models(get_app(app))))

#             ignored_models = settings.LANDLORD_ROUTER_IGNORED_MODELS
#             for model in ignored_models:
#                 models.add(get_model(*model.split('.')))

#             self.__ignored_models = tuple(models)
#             logger.info('Ignored models: %s', self.__ignored_models)
#         return self.__ignored_models

#     def db_for_read(self, model, **hints):
#         if model in self.ignored_models:
#             return None

#         tenant = hints.get(settings.LANDLORD_DEFAULT_TENANT_KEY, landlord.get_current_tenant())
#         if tenant:
#             return unicode(tenant)

#     def db_for_write(self, model, **hints):
#         if model in self.ignored_models:
#             return None

#         tenant = hints.get(settings.LANDLORD_DEFAULT_TENANT_KEY, landlord.get_current_tenant())
#         if tenant:
#             return str(tenant)

#     def allow_syncdb(self, db, model):
#         if db in ['default']:
#             return True

#         if model in self.ignored_models:
#             logger.info('Ignoring syncdb on %s for database %s', model, db)
#             return False

    # def allow_relation(self, obj1, obj2, **hints):
        # settings.LANDLORD_ROUTER_RELATION_IGNORE
        # return landlord.current_tenant
        # print 'allow_relation: ', obj1, obj2, hints

# import logging
# logger = logging.getLogger(__name__)

def enable_router_hints():
    import new
    from django.db import DEFAULT_DB_ALIAS, router
    from landlord.conf import settings

    def _router_func(action):
        def _route_db(self, model, **hints):
            from landlord import landlord
            hints.update({
                settings.LANDLORD_DEFAULT_NAMESPACE_KEY: landlord.get_current_namespace(),
            })

            chosen_db = None
            for router in self.routers:
                try:
                    method = getattr(router, action)
                except AttributeError:
                    # If the router doesn't have a method, skip to the next one.
                    pass
                else:
                    chosen_db = method(model, **hints)
                    if chosen_db:
                        return chosen_db
            try:
                return hints['instance']._state.db or DEFAULT_DB_ALIAS
            except KeyError:
                return DEFAULT_DB_ALIAS
        return _route_db
    router.db_for_read = new.instancemethod(_router_func('db_for_read'), router, None)
    router.db_for_write = new.instancemethod(_router_func('db_for_write'), router, None)