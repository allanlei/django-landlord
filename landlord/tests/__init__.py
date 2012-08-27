from django.dispatch import receiver
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from landlord import landlord, residence
from landlord.signals import *

from landlord.tests.utils import randomStr
from landlord.tests.decorators import test_concurrently

import tempfile
import unittest
import threading
import subprocess
import random
import json
import logging
logger = logging.getLogger(__name__)


@receiver(tenant_created, dispatch_uid='landlord_tenant_syncdb')
def setup_database_for_tenant(sender, instance, **kwargs):
    call_command('syncdb', verbosity=0, interactive=False, database=instance.name)


class LandlordBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.tenants = [tenant.name for tenant in residence]

    def check(self):
        for tenant_id in self.tenants:
            query = User.objects.using(tenant_id).exclude(username__startswith=tenant_id + '-')
            if query.exists():
                logger.warn('Incorrect .using(): %s', tenant_id)
                for user in query:
                    logger.warn('\t %s', user.username)
            self.assertFalse(query.exists())

        for tenant_id in self.tenants:
            credentials = {'name': tenant_id}
            with residence.get(**credentials):
                query = User.objects.exclude(username__startswith=tenant_id)
                if query.exists():
                    logger.warn('Incorrect (with statement): %s', credentials)
                    for user in query:
                        logger.warn('\t %s', user.username)
                self.assertFalse(query.exists())

    def get_random_tenant_credentials(self):
        return {
            'name': random.choice(self.tenants)
        }

    def tearDown(self):
        self.check()


class FunctionBlock(unittest.TestCase):
    def setUp(self):
        self.tenants = [tenant.name for tenant in residence]

    def get_random_tenant_credentials(self):
        return {
            'name': random.choice(self.tenants)
        }

    def test_basic(self, iterations=100):
        for i in range(iterations):
            credentials = self.get_random_tenant_credentials()
            with residence.get(**credentials) as tenant:
                tenant_id = credentials['name']
                User.objects.create(username=tenant_id + '-' + randomStr())

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())


    def test_recursive(self, depth=100):
        credentials = self.get_random_tenant_credentials()

        with residence.get(**credentials):
            tenant_id = credentials['name']
            User.objects.create(username=tenant_id + '-' + randomStr())
            if depth > 0:
                self.test_recursive(depth=depth-1)
            User.objects.create(username=tenant_id + '-' + randomStr())

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())

    def test_basic_concurrent(self, concurrency=10):
        def test(credentials):
            with residence.get(**credentials) as tenant:
                tenant_id = credentials['name']
                User.objects.create(username=tenant_id + '-' + randomStr())

        threads = []
        for i in range(concurrency):
            thread = threading.Thread(target=test, args=(self.get_random_tenant_credentials(), ))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())

    def test_recursive_concurrent(self, concurrency=10):
        def test(tenants, depth=100):
            credentials = {
                'name': random.choice(tenants),
            }

            with residence.get(**credentials):
                tenant_id = credentials['name']
                User.objects.create(username=tenant_id + '-' + randomStr())
                if depth > 0:
                    test(tenants, depth=depth-1)
                User.objects.create(username=tenant_id + '-' + randomStr())

        threads = []
        for i in range(concurrency):
            thread = threading.Thread(target=test, args=(list(self.tenants), ))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())


class RequestCycle(unittest.TestCase):
    def setUp(self):
        self.tenants = [tenant.name for tenant in residence]

    def test_basic(self, iterations=200):
        for i in range(iterations):
            client = Client()
            tenant = random.choice(self.tenants)
            username = tenant + '-' + randomStr()
            url = '{url}?tenant={tenant}&username={username}'.format(
                url=reverse('user:create'), 
                tenant=tenant, 
                username=username,
            )
            logger.info('requesting: %s', url)
            response = client.post(url)
            data = json.loads(response.content)

            self.assertEqual(response.status_code, 200)

            self.assertEqual(User.objects.using(tenant).get(pk=data['pk']).username, username)
            with residence.get(**{'name': tenant}):
                self.assertEqual(User.objects.get(pk=data['pk']).username, username)

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())

    def test_recursive(self, iterations=200):
        for i in range(iterations):
            client = Client()
            tenant = random.choice(self.tenants)
            username = tenant + '-' + randomStr()
            url = '{url}?tenant={tenant}&username={username}'.format(
                url=reverse('user:create_random'), 
                tenant=tenant, 
                username=username,
            )
            logger.info('requesting: %s', url)
            response = client.post(url)
            data = json.loads(response.content)

            self.assertEqual(response.status_code, 200)

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())

    def test_concurrent(self, concurrency=10):
        def test(tenants, iterations=100):
            for i in range(iterations):
                client = Client()
                tenant = random.choice(tenants)
                username = tenant + '-' + randomStr()
                url = '{url}?tenant={tenant}&username={username}'.format(
                    url=reverse('user:create'), 
                    tenant=tenant, 
                    username=username,
                )
                logger.info('requesting: %s', url)
                response = client.post(url)
                data = json.loads(response.content)

                self.assertEqual(response.status_code, 200)

                self.assertEqual(User.objects.using(tenant).get(pk=data['pk']).username, username)
                with residence.get(**{'name': tenant}):
                    self.assertEqual(User.objects.get(pk=data['pk']).username, username)

        threads = []
        for i in range(concurrency):
            thread = threading.Thread(target=test, args=(list(self.tenants), ))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())

    def test_recursive_concurrent(self, concurrency=10):
        def test(tenants):
            client = Client()
            tenant = random.choice(tenants)
            username = tenant + '-' + randomStr()
            url = '{url}?tenant={tenant}&username={username}'.format(
                url=reverse('user:create_random'), 
                tenant=tenant, 
                username=username,
            )
            logger.info('requesting: %s', url)
            response = client.post(url)
            data = json.loads(response.content)

            self.assertEqual(response.status_code, 200)

        threads = []
        for i in range(concurrency):
            thread = threading.Thread(target=test, args=(list(self.tenants), ))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for tenant in self.tenants:
            self.assertFalse(User.objects.using(tenant).exclude(username__startswith=tenant).exists())

            with residence.get(name=tenant):
                self.assertFalse(User.objects.exclude(username__startswith=tenant).exists())

class Templates(unittest.TestCase):
    pass