from django.test.simple import DjangoTestSuiteRunner

from landlord.tests.utils import randomStr

import glob
import os


class LandlordTestRunner(DjangoTestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        from landlord import residence

        for i in range(10):
            tenant_id = '{domain}.com'.format(domain=randomStr())
            tenant = residence.create(name=tenant_id)        #residence.find()
        return super(LandlordTestRunner, self).run_suite(suite, **kwargs)

    def teardown_databases(self, old_config, **kwargs):
        response = super(LandlordTestRunner, self).teardown_databases(old_config, **kwargs)
        filelist = glob.glob('*.db')
        for f in filelist:
            os.remove(f)
        return response