import unittest
from scripts.run_tvs_optical_laterality import contacts

class ContactsTest(unittest.TestCase):
    def test_explicit_sides_and_dedup(self):
        b={'InitialContact_Event':[1.,2.],'InitialContact_LeftRight':['Right','Left']}
        self.assertEqual(contacts({'ContinuousWalkingPeriod':[b,b]}),[(1.,1),(2.,0)])
    def test_conflict(self):
        with self.assertRaises(ValueError):
            contacts({'ContinuousWalkingPeriod':{'InitialContact_Event':[1.,1.],'InitialContact_LeftRight':['Left','Right']}})
    def test_empty(self):self.assertEqual(contacts({}),[])

if __name__=='__main__':unittest.main()
