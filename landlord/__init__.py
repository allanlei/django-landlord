# from django.core.urlresolvers import get_callable

from landlord.conf import settings
from landlord.signals import landlord_initized, namespace_removed, namespace_added, namespace_changed, namespace_peaked

import threading
import Queue
import logging
logger = logging.getLogger(__name__)


class Landlord(threading.local):
    def __init__(self, queue=None):
        self.__queue = Queue.LifoQueue(maxsize=0)
        if not self.queue:
            raise Exception('Queue required for Landlord instances')
        landlord_initized.send(sender=self, thread=threading.current_thread())

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

    def push(self, namespace):
        current_namespace = self.get_current_namespace()
        self.queue.put_nowait(namespace)
        namespace_added.send(sender=self, namespace=namespace)
        if namespace != current_namespace:
            namespace_changed.send(sender=self, namespace=namespace, from_namespace=current_namespace)
        return namespace

    def pop(self):
        namespace = self.queue.get_nowait()
        namespace_removed.send(sender=self, namespace=namespace)
        current_namespace = self.get_current_namespace()
        if current_namespace != namespace:
            namespace_changed.send(sender=self, namespace=current_namespace, from_namespace=namespace)
        return namespace

    # TODO
    # def remove(self, namespace)

    def peak(self):
        # Not thread safe, but since we are using threading.local(), it should be acceptable
        namespace = self.queue.queue[-1] if len(self.queue.queue) > 0 else None
        namespace_peaked.send(sender=self, namespace=namespace)
        return namespace

    def get_current_namespace(self):
        return self.peak()

    def __contains__(self, namespace):
        return namespace in self.queue.queue

    def __iter__(self):
        for obj in self.queue.queue:
            yield obj

    def __len__(self):
      return self.size()


landlord = Landlord()