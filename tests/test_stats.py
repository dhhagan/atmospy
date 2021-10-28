import unittest
import atmospy.stats as stats
import pandas as pd
import numpy as np
import os

datadir = "datafiles/"

class TestClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_regression(self):
        # load some data
        test = pd.read_csv(
                        os.path.join(datadir,'regression_test.csv')
                        )
        assert isinstance(test, pd.DataFrame)

        # list, np array, series, df[col] test cases

        #pd.DataFrame and column names case
        self.test_generic(x='internal', y='reference', data=test)

        #pd.Series case
        self.test_generic(x=test['internal'], y=test['reference'])

        #arrays case
        self.test_generic(x=test['internal'].to_numpy(), y=test['reference'].to_numpy())

        #list case
        self.test_generic(x=test['internal'].to_list(), y=test['reference'].to_list())

    
    def test_generic(self, **kwargs):
        #load kwargs
        x = kwargs.pop("x")
        y = kwargs.pop("y")
        data = kwargs.pop("data", None)
        statstest = stats.stats(x=x, y=y, data=data)

        #make sure all data is there in correct format
        self.assertIsInstance(statstest, dict)
        self.assertTrue("mae" in statstest.keys())
        #still need to add
        #self.assertTrue("cvmae" in statstest.keys())
        self.assertTrue("mape" in statstest.keys())
        self.assertTrue("mbe" in statstest.keys())
        self.assertTrue("rmse" in statstest.keys())
        self.assertTrue("mdae" in statstest.keys())
        self.assertTrue("r2_score" in statstest.keys())

        #make sure the values are correct
        self.assertGreaterEqual(statstest["mae"], 3.0)
        self.assertLessEqual(statstest["mae"], 3.1)
        self.assertGreaterEqual(statstest["mape"], 0.31)
        self.assertLessEqual(statstest["mape"], 0.33)
        self.assertGreaterEqual(statstest["mbe"], 2.9)
        self.assertLessEqual(statstest["mbe"], 3.1)
        self.assertGreaterEqual(statstest["rmse"], 3.7)
        self.assertLessEqual(statstest["rmse"], 3.8)
        self.assertGreaterEqual(statstest["mdae"], 2.5)
        self.assertLessEqual(statstest["mdae"], 2.6)
        self.assertGreaterEqual(statstest["r2_score"], 0.35)
        self.assertLessEqual(statstest["r2_score"], 0.37)


    def test_epa(self):
        #load some data
        test = pd.read_csv(
                        os.path.join(datadir,'epa_test.csv')
                        )
        assert isinstance(test, pd.DataFrame)
        
        return
