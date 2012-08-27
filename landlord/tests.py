from landlord import landlord

# from utils import randomStr

import string
import random
import unittest
import logging
logger = logging.getLogger(__name__)

def randomStr(length=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(length))





class LandlordTestCase(unittest.TestCase):
    def test_basic(self):
        random_str = randomStr(24)
        landlord.push(random_str)
        self.assertEqual(landlord.get_current_namespace(), random_str)
        landlord.pop()
        self.assertEqual(landlord.get_current_namespace(), None)

    def test_tracker(self):
        from landlord.models import LandlordTrackingMixin

        class TestClass(LandlordTrackingMixin):
            pass

        obj = TestClass()
        with obj:
            pass