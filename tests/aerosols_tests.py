import unittest
import atmospy
import pandas as pd
import os
import statsmodels.api as sm

def linear_eval(X1, X2):
    '''Perform evaluation (slope, r2) on a linear model
    '''
    df = pd.DataFrame.from_dict({'X1': X1, 'X2': X2}).dropna(how = 'any')

    model   = sm.OLS(df.X2, df.X1)
    results = model.fit()

    return (results.params[0], results.rsquared)

class SetupTestCase(unittest.TestCase):
    def setUp(self):

        self.number     = atmospy.io.SMPS()
        self.log_number = atmospy.io.SMPS()
        self.diameter   = atmospy.io.SMPS()
        self.surface    = atmospy.io.SMPS()
        self.volume     = atmospy.io.SMPS()

        self.number.load(os.path.join(os.getcwd(), "tests/data/SMPS_Number.txt"))
        self.log_number.load(os.path.join(os.getcwd(), "tests/data/SMPS_Log_Number.txt"))
        self.diameter.load(os.path.join(os.getcwd(), "tests/data/SMPS_Log_Diameter.txt"))
        self.surface.load(os.path.join(os.getcwd(), "tests/data/SMPS_Log_Surface.txt"))
        self.volume.load(os.path.join(os.getcwd(), "tests/data/SMPS_Log_Volume.txt"))

    def tearDown(self):
        pass

    def test_generic_smps(self):
        threshold = 0.99
        lbounds = 0.99
        ubounds = 1.01

        # Create the distribution and run the stats
        d = atmospy.aerosols.ParticleDistribution(histogram = self.number.histogram, bins = self.number.bins)

        d.compute()
        d.statistics()

        # Now that we've performed the calculations, make sure they're correct!
        # Number-weighted first...
        res_num1 = linear_eval(self.number.data['Total Concentration'], d.stats['Number', :, 'N Total'])
        res_num2 = linear_eval(self.number.data['Mean'], d.stats['Number', :, 'Mean'])
        res_num3 = linear_eval(self.number.data['Geo. Mean'], d.stats['Number', :, 'GM'])
        res_num4 = linear_eval(self.number.data['Geo Std Dev'], d.stats['Number', :, 'GSD'])

        self.assertTrue(res_num1[0] >= lbounds and res_num1[0] <= ubounds and res_num1[1] >= threshold)
        self.assertTrue(res_num2[0] >= lbounds and res_num2[0] <= ubounds and res_num2[1] >= threshold)
        self.assertTrue(res_num3[0] >= lbounds and res_num3[0] <= ubounds and res_num3[1] >= threshold)
        self.assertTrue(res_num4[0] >= lbounds and res_num4[0] <= ubounds and res_num4[1] >= threshold)

        # Diameter-weighted first...
        res_diam1 = linear_eval(self.diameter.data['Mean'], d.stats['Diameter', :, 'Mean'])
        res_diam2 = linear_eval(self.diameter.data['Geo. Mean'], d.stats['Diameter', :, 'GM'])
        res_diam3 = linear_eval(self.diameter.data['Geo Std Dev'], d.stats['Diameter', :, 'GSD'])

        self.assertTrue(res_diam1[0] >= lbounds and res_diam1[0] <= ubounds and res_diam1[1] >= threshold)
        self.assertTrue(res_diam2[0] >= lbounds and res_diam2[0] <= ubounds and res_diam2[1] >= threshold)
        self.assertTrue(res_diam3[0] >= lbounds and res_diam3[0] <= ubounds and res_diam3[1] >= threshold)

        # Surface Area-weighted first...
        res_sa1 = linear_eval(self.surface.data['Mean'], d.stats['Surface Area', :, 'Mean'])
        res_sa2 = linear_eval(self.surface.data['Geo. Mean'], d.stats['Surface Area', :, 'GM'])
        res_sa3 = linear_eval(self.surface.data['Geo Std Dev'], d.stats['Surface Area', :, 'GSD'])

        self.assertTrue(res_sa1[0] >= lbounds and res_sa1[0] <= ubounds and res_sa1[1] >= threshold)
        self.assertTrue(res_sa2[0] >= lbounds and res_sa2[0] <= ubounds and res_sa2[1] >= threshold)
        self.assertTrue(res_sa3[0] >= lbounds and res_sa3[0] <= ubounds and res_sa3[1] >= threshold)

        # Volume-weighted first...
        res_vol1 = linear_eval(self.volume.data['Mean'], d.stats['Volume', :, 'Mean'])
        res_vol2 = linear_eval(self.volume.data['Geo. Mean'], d.stats['Volume', :, 'GM'])
        res_vol3 = linear_eval(self.volume.data['Geo Std Dev'], d.stats['Volume', :, 'GSD'])

        self.assertTrue(res_vol1[0] >= lbounds and res_vol1[0] <= ubounds and res_vol1[1] >= threshold)
        self.assertTrue(res_vol2[0] >= lbounds and res_vol2[0] <= ubounds and res_vol2[1] >= threshold)
        self.assertTrue(res_vol3[0] >= lbounds and res_vol3[0] <= ubounds and res_vol3[1] >= threshold)

    def test_log_number_smps(self):
        threshold   = 0.99
        ubounds     = 1.01
        lbounds     = 0.99

        d = atmospy.aerosols.ParticleDistribution( histogram = self.log_number.histogram, bins = self.log_number.bins )

        d.compute()
        d.statistics()

        # Now that we've performed the calculations, make sure they're correct!
        # Number-weighted first...
        res_num1 = linear_eval(self.number.data['Total Concentration'], self.log_number.data['Total Concentration'])
        res_num2 = linear_eval(self.number.data['Mean'], d.stats['Number', :, 'Mean'])
        res_num3 = linear_eval(self.number.data['Geo. Mean'], d.stats['Number', :, 'GM'])
        res_num4 = linear_eval(self.number.data['Geo Std Dev'], d.stats['Number', :, 'GSD'])

        self.assertTrue(res_num1[0] >= lbounds and res_num1[0] <= ubounds and res_num1[1] >= threshold)
        self.assertTrue(res_num2[0] >= lbounds and res_num2[0] <= ubounds and res_num2[1] >= threshold)
        self.assertTrue(res_num3[0] >= lbounds and res_num3[0] <= ubounds and res_num3[1] >= threshold)
        self.assertTrue(res_num4[0] >= lbounds and res_num4[0] <= ubounds and res_num4[1] >= threshold)

        # Diameter-weighted first...
        res_diam1 = linear_eval(self.diameter.data['Mean'], d.stats['Diameter', :, 'Mean'])
        res_diam2 = linear_eval(self.diameter.data['Geo. Mean'], d.stats['Diameter', :, 'GM'])
        res_diam3 = linear_eval(self.diameter.data['Geo Std Dev'], d.stats['Diameter', :, 'GSD'])

        self.assertTrue(res_diam1[0] >= lbounds and res_diam1[0] <= ubounds and res_diam1[1] >= threshold)
        self.assertTrue(res_diam2[0] >= lbounds and res_diam2[0] <= ubounds and res_diam2[1] >= threshold)
        self.assertTrue(res_diam3[0] >= lbounds and res_diam3[0] <= ubounds and res_diam3[1] >= threshold)

        # Surface Area-weighted first...
        res_sa1 = linear_eval(self.surface.data['Mean'], d.stats['Surface Area', :, 'Mean'])
        res_sa2 = linear_eval(self.surface.data['Geo. Mean'], d.stats['Surface Area', :, 'GM'])
        res_sa3 = linear_eval(self.surface.data['Geo Std Dev'], d.stats['Surface Area', :, 'GSD'])

        self.assertTrue(res_sa1[0] >= lbounds and res_sa1[0] <= ubounds and res_sa1[1] >= threshold)
        self.assertTrue(res_sa2[0] >= lbounds and res_sa2[0] <= ubounds and res_sa2[1] >= threshold)
        self.assertTrue(res_sa3[0] >= lbounds and res_sa3[0] <= ubounds and res_sa3[1] >= threshold)

        # Volume-weighted first...
        res_vol1 = linear_eval(self.volume.data['Mean'], d.stats['Volume', :, 'Mean'])
        res_vol2 = linear_eval(self.volume.data['Geo. Mean'], d.stats['Volume', :, 'GM'])
        res_vol3 = linear_eval(self.volume.data['Geo Std Dev'], d.stats['Volume', :, 'GSD'])

        self.assertTrue(res_vol1[0] >= lbounds and res_vol1[0] <= ubounds and res_vol1[1] >= threshold)
        self.assertTrue(res_vol2[0] >= lbounds and res_vol2[0] <= ubounds and res_vol2[1] >= threshold)
        self.assertTrue(res_vol3[0] >= lbounds and res_vol3[0] <= ubounds and res_vol3[1] >= threshold)
