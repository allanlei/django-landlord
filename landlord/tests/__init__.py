from django.dispatch import receiver
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse

from landlord import landlord, residence
from landlord.signals import *

from landlord.tests.utils import randomStr
from landlord.tests.decorators import test_concurrently

import unittest
import threading
import random
import json


@receiver(tenant_created, dispatch_uid='landlord_tenant_syncdb')
def setup_database_for_tenant(sender, instance, **kwargs):
    call_command('syncdb', verbosity=0, interactive=False, database=instance.name)


class LandlordBaseTestCase(unittest.TestCase):
    def setUp(self):
        # self.tenants = list(residence)# -> List containing all Tenants living in the storage

        from landlord.models import Tenant
        self.tenants = [tenant.name for tenant in Tenant.objects.using('default').order_by('?')]

    def check(self):
        for tenant_id in self.tenants:
            query = User.objects.using(tenant_id).exclude(username__startswith=tenant_id + '-')
            if query.exists():
                print 'Incorrect .using(): ', tenant_id
                for user in query:
                    print '\t', user.username
            self.assertFalse(query.exists())

        for tenant_id in self.tenants:
            credentials = {'name': tenant_id}
            with residence.get(**credentials):
                query = User.objects.exclude(username__startswith=tenant_id)
                if query.exists():
                    print 'Incorrect (with statement): ', credentials
                    for user in query:
                        print '\t', user.username
                self.assertFalse(query.exists())

    def get_random_tenant_credentials(self):
        return {
            'name': random.choice(self.tenants)
        }

    def tearDown(self):
        self.check()


class LandlordFunctionBlockTestCase(LandlordBaseTestCase):
    def test_function_block(self, iterations=100):
        for i in range(iterations):
            credentials = self.get_random_tenant_credentials()
            with residence.get(**credentials):
                tenant_id = credentials['name']
                User.objects.create(username=tenant_id + '-' + randomStr())

    def test_function_block_recursive(self, depth=100):
        credentials = self.get_random_tenant_credentials()

        with residence.get(**credentials):
            tenant_id = credentials['name']
            User.objects.create(username=tenant_id + '-' + randomStr())
            if depth > 0:
                self.test_function_block_recursive(depth=depth-1)
            User.objects.create(username=tenant_id + '-' + randomStr())

    def test_function_block_concurrent(self):
        # @test_concurrently(15)    Not django test case doesnt work in threaded mode?
        def test(tenants):
            for i in range(10):
                credentials = {
                    'name': random.choice(tenants)
                }
                with residence.get(**credentials):
                    tenant_id = credentials['name']
                    User.objects.create(username=tenant_id + '-' + randomStr())
        test(self.tenants)

class LandlordRequestCycleTestCase(LandlordBaseTestCase):
    def tearDown(self):
        pass

    def test_request(self, iterations=1000):
        for i in range(iterations):
            client = Client()
            tenant = random.choice(self.tenants)
            username = randomStr()
            url = '{url}?tenant={tenant}&username={username}'.format(url=reverse('user:create'), tenant=tenant, username=username)
            print 'Requesting: ', url
            response = client.post(url)
            data = json.loads(response.content)
            print 'data: ', data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['tenant'], tenant)

            self.assertTrue(User.objects.using(tenant).get(pk=data['pk']).username == data['username'])
            self.assertEqual(User.objects.using(tenant).get(pk=data['pk']).username, username)

            with residence.get(**{'name': tenant}):
                self.assertTrue(User.objects.get(pk=data['pk']).username == data['username'])
                self.assertEqual(User.objects.get(pk=data['pk']).username, username)
        
class LandlordCommandsTestCase(LandlordBaseTestCase):
    pass