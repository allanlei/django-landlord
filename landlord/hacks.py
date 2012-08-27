from landlord import DEFAULT_TENANT_KEY


import logging
logger = logging.getLogger(__name__)

def add_tenant_to_router_hints():
    import new
    from django.db import DEFAULT_DB_ALIAS

    def _router_func(action):
        def _route_db(self, model, **hints):
            from landlord import landlord
            hints.update({
                DEFAULT_TENANT_KEY: landlord.get_current_tenant(),
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



from django.db import router, connections

import collections
import threading

class LandlordDatabaseController(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.size_limit = int(kwargs.pop('size_limit')) if 'size_limit' in kwargs else None
        self.store = dict()
        self.landlord_store = threading.local()
        self.update(dict(*args, **kwargs))

    # def ensure_size_limit(self):
        # pass
        # if self.size_limit is not None:
            # while len(self) > self.size_limit:
                # self.popitem(last=False)

    def __getitem__(self, key):
        original_key, key = self.__keytransform__(key), key
        # logger.debug('GET: ' + key)

        if key not in self.store:
            if not hasattr(self.landlord_store, key):
                from landlord import residence

                tenant = residence.get(name=key)
                if tenant:
                    db = settings.DATABASES['default'].copy()
                    # db['NAME'] = str(tenant)
                    setattr(self.landlord_store, key, db)
            return getattr(self.landlord_store, key)
        return self.store[key]

    def __setitem__(self, key, value):
        original_key, key = self.__keytransform__(key), key
        # logger.debug('SET: ' + key + value)

        if key not in self.store:
            if hasattr(self.landlord_store, key):
                setattr(self.landlord_store, key, value)    #Write the value back to Tenant instead of saving to dict
                return
        self.store[key] = value

    def __delitem__(self, key):
        original_key, key = self.__keytransform__(key), key
        # logger.debug('DEL: ', key)

        if key not in self.store:
            if key in self.landlord_store:
                delattr(self.landlord_store, key)
                return
        del self.store[key]
        
    def __keytransform__(self, key):
        return key

    def __iter__(self):
        from landlord import residence

        entries = dict(self.store.items())
        # print entries
        for tenant in residence:
            db = getattr(self.landlord_store, tenant.name, None)
            if db:
                entries.update({
                    tenant.name: db,
                })
        # print entries
        # print 'OK'
        return iter(entries)

    def __len__(self):
        return len(self.store) + len(self.landlord_store)

    def __unicode__(self):
        return unicode(self.store)

    def __str__(self):
        return unicode(self)


from django.conf import settings
settings.DATABASES = LandlordDatabaseController(settings.DATABASES)
connections.databases = settings.DATABASES