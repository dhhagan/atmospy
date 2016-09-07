import unittest
import atmospy
import pandas as pd
import os

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_smps_loader(self):
        # Load a generic dN dataset
        tmp = atmospy.io.SMPS()

        self.assertEqual(tmp.multiplier, 64)

        print (os.getcwd())
        tmp.load(os.path.join(os.getcwd(), "tests/data/SMPS_Number.txt"))

        self.assertEqual(tmp.bins.shape[1], 3)
        self.assertIsNotNone(tmp.histogram)
        self.assertIsNotNone(tmp.data)
