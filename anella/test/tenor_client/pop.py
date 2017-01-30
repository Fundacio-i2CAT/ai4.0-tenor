import unittest
import sys
sys.path.append('../../tenor_client/')
import tenor_pop

class PopTestCase(unittest.TestCase):
    def runTest(self):
	b = tenor_pop.TenorPoP(2)
        print b.get_limits()['absolute']['maxSecurityGroups']        
        print b.get_network_quota_details()
        print b.get_routers_details()
        #print b.get_secutity_groups_details()
        #pop = TenorPoP()
        self.assertEqual(50, 50)
