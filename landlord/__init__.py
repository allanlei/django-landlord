from django.core.urlresolvers import get_callable

from landlord.conf import settings
from landlord.signals import *

import threading
import Queue


class Landlord(threading.local):
    '''
    Landlord is a tenant manager for each thread. Keeps track of current_tenant by using LIFO stack.
    Each thread gets 1 instance of Landlord by default. Doesn't __init__ until it is used.

    Thread-safe LIFO stack/Queue.LifoQueue(max_size=-1)
    Tenant.enter = landlord.put(self)
    __exit__ = landlord.get()

    if using Queue.Queue:
        needs a queue per thread
        implement:
            qsize() -> self.queue.qsize()
            empty() -> self.queue.empty()
            full() -> self.queue.full()
            put() -> self.queue.put()
            get() -> self.queue.get()
            get_current_tenant() -> peak() -> self.queue.queue[-1]
            # Not thread safe, but since we are using threading.local(), it shoudl be ok

    Storage: Non-persistent
    Thread-safety: required
    '''
    def __init__(self, queue=None):
        self.__queue = Queue.LifoQueue(maxsize=0)
        if not self.queue:
            raise Exception('Queue required for Landlord instances')
        landlord_init.send(sender=self, thread=threading.current_thread())

    @property
    def ident(self):
        return threading.current_thread().ident

    @property
    def queue(self):
        return self.__queue

    def size(self):
        return self.queue.qsize()

    def is_empty(self):
        return self.queue.empty()

    def is_full(self):
        return self.queue.full()

    def put(self, tenant):
        # landlord_current_tenant_pre_change.send(sender=self, tenant=tenant)
        return self.queue.put(tenant)
        # landlord_current_tenant_changed.send(sender=self, tenant=self.current_tenant)

    def get(self):
        # landlord_current_tenant_pre_change.send(sender=self, tenant=tenant)
        return self.queue.get()
        # landlord_current_tenant_changed.send(sender=self, tenant=self.current_tenant)

    push = put
    pop = get       #Should be able to landlord.remove(tenant)

    def peak(self):
        # Not thread safe, but since we are using threading.local(), it should be acceptable
        return self.queue.queue[-1] if len(self.queue.queue) > 0 else None

    def get_current_tenant(self):
        return self.peak()

    # def __contains__(self, tenant):
    #   Query backend for Tenant

    def __len__(self):
      return self.size()



#Initialize default instances
if settings.LANDLORD_DEFAULT_INSTANCES:
    from landlord.residence import Residence
    landlord = Landlord()
    residence = Residence()