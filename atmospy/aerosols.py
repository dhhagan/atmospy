from .errors import DataFormatError

import pandas as pd
import numpy as np
import warnings
import math

class ParticleDistribution(object):
    """Generic Particle Distribution

    dN: Pandas DataFrame with histogram information only
    bins: 2D numpy array with [[left_boundary_i, right_boundary_i]]
    """
    def __init__(self, **kwargs):
        self.density    = kwargs.pop('density', 1.65)
        self.bins       = kwargs.pop('bins')
        self._divisor   = kwargs.pop('divisor', 100.)

        self.dN         = kwargs.pop('dN')
        self.stats      = pd.DataFrame()

        # Make sure the data is in the correct format
        if type(self.dN) is not pd.DataFrame:
            raise DataFormatError("You must supply a Pandas DataFrame")

        # Make sure that bins is a 2D numpy array
        if type(self.bins) is not np.ndarray or self.bins.shape[1] != 2:
            raise DataFormatError("Bins must be a 2D Numpy Array")

        # Make sure the length of bins is len(columns) + 1
        if self.bins.shape[0] != len(self.dN.columns):
            raise DataFormatError("There must be one bin per histogram column")

        # Rename the index
        self.dN.index.rename('index', inplace = True)

        # Replace all zeros with NaN's and drop empty rows
        self.dN = self.dN.replace(0, np.nan).dropna(how = 'all')

        # Make sure there are no duplicate rows
        self.dN = self.dN.reset_index().drop_duplicates('index').set_index('index')

        # Calculate some variables
        self.info = pd.DataFrame.from_dict({
            'left': self.bins[:, 0],
            'right': self.bins[:, 1]
            })

        self.info['dDp']    = self.info['right'] - self.info['left']
        self.info['Dp']     = self.info.apply(lambda x: np.mean([x['left'], x['right']]), axis = 1)
        self.info['logDp']  = self.info['Dp'].apply(np.log10)
        self.info['dlogDp'] = self.info.apply(lambda x: np.log10(x['right'] - np.log10(x['left'])) , axis = 1)

        self.Dp             = self.info['Dp']
        self.dDp            = self.info['dDp']
        self.logDp          = self.info['logDp']
        self.dlogDp         = self.info['dlogDp']

        self.s_factor = self.Dp ** 2 * math.pi
        self.v_factor = self.Dp ** 3 * (math.pi / 6.)
        self.m_factor = self.v_factor * self.density

        # Set the primary statistics
        self.data = self.calculate(self.dN)

    def calculate(self, dN):
        """Calculate all of the statistics and set them
        """
        # Calculate according to S&P 8.4, 8.5
        dS          = dN.mul(self.s_factor.values)
        dV          = dN.mul(self.v_factor.values)
        dM          = dN.mul(self.m_factor.values)

        dNdDp       = dN.div(self.dDp.values)
        dSdDp       = dS.div(self.dDp.values)
        dVdDp       = dV.div(self.dDp.values)
        dMdDp       = dM.div(self.dDp.values)

        dNdlogDp    = dNdDp.mul(2.303).mul(self.Dp.values)  # S&P 8.18
        dSdlogDp    = dSdDp.mul(2.303).mul(self.Dp.values)  # S&P 8.19
        dVdlogDp    = dVdDp.mul(2.303).mul(self.Dp.values)  # S&P 8.20
        dMdlogDp    = dMdDp.mul(2.303).mul(self.Dp.values)  # S&P 8.20

        # Integrate bin-wise
        dN_area     = dNdlogDp.mul(self.dlogDp.values)
        dS_area     = dSdlogDp.mul(self.dlogDp.values)
        dV_area     = dVdlogDp.mul(self.dlogDp.values)
        dM_area     = dMdlogDp.mul(self.dlogDp.values)

        # Dump everything into a panel
        data = pd.Panel({
            'dN':       dN,
            'dS':       dS,
            'dV':       dV,
            'dM':       dM,
            'dNdDp':    dNdDp,
            'dSdDp':    dSdDp,
            'dVdDp':    dVdDp,
            'dMdDp':    dMdDp,
            'dNdlogDp': dNdlogDp,
            'dSdlogDp': dSdlogDp,
            'dVdlogDp': dVdlogDp,
            'dMdlogDp': dMdlogDp,
            'dN_area':  dN_area,
            'dS_area':  dS_area,
            'dV_area':  dV_area,
            'dM_area':  dM_area
            }).transpose(1, 2, 0)

        return data

    def subset(self, cutoff = None):
        """Return a subset of dN based on the diameter cutoff in micrometers
        """
        if cutoff is None:
            return self.dN

        # Locate the index of the bin that must be selected
        i = self.info.query("left < {}".format(cutoff)).index[-1]

        f = (cutoff - (self.info.loc[i]['left'])) / (self.info.loc[i]['right'] - self.info.loc[i]['left'])

        # Recalculate the Last bin and return just the subset dN
        d = self.data[:, 'bin0':'bin{}'.format(i), ['dN', 'dS', 'dV', 'dM']].copy()

        d.ix[:, 'bin{}'.format(i)] = d[:, 'bin{}'.format(i), :].mul(f)

        return d

    def integrated_mass(self, cutoff):
        """Return a Series with the PM cutoff of interest
        """
        tmp = self.subset(cutoff)

        return tmp[:, :, 'dM'].sum()

    def _variance(self, row):
        """
        Calculate the value of (each bin - arithmetic mean) ** 2 as a factor and then
        multiply by the number concentration in that bin before multiplying by 1 / Ntot
        """
        ntot = row.sum()
        mean = row.mul(self.Dp.values).sum() / ntot

        return row.mul((self.Dp.values - mean) **2).sum() / ntot

    def statistics(self, dN):
        """Calculate the particle distribution statistics of dN (assumes dN is in #/cm3)
        """
        stats = pd.DataFrame()

        stats['ntot']  = dN.sum(axis = 1)
        stats['mean']  = dN.mul(self.Dp.values).sum(axis = 1) / stats['ntot']
        stats['var']   = dN.apply(self._variance, axis = 1)

        # The divisor trick deals with large numbers...
        stats['cmd']   = (dN.apply(lambda x: self.Dp.values ** (x / self._divisor), axis = 1).replace(0, np.nan).prod(axis = 1).pow(1. / (stats['ntot'] / self._divisor)))

        # Calculate the geometric standard deviation per S&P
        for i, row in stats.iterrows():
            nrow = dN.ix[i]
            try:
                stats.loc[i, 'gsd'] = math.pow(10, np.sqrt(nrow.mul((self.logDp.values - np.log10(row['cmd'])) ** 2).sum() / (row['ntot'] - 1)))
            except Exception as e:
                stats.loc[i, 'gsd'] = np.nan

        # Calculate the SA CMD using S&P 8.50
        stats['cmd_SA'] = stats.apply(lambda x: np.exp(np.log(x['cmd']) + 2 * np.log(x['gsd']) ** 2), axis = 1)

        return stats

    def __repr__(self):
        return "Particle Distribution"

class AlphasenseOPCN2(ParticleDistribution):
    """
    """
    def __init__(self, dN, **kwargs):
        # Bin Boundaries for the Alphasense OPC-N2 in micrometers
        bins = np.array([
            [0.38, 0.54],
            [0.54, 0.78],
            [0.78, 1.05],
            [1.05, 1.34],
            [1.34, 1.59],
            [1.59, 2.07],
            [2.07, 3.],
            [3., 4.],
            [4., 5.],
            [5., 6.5],
            [6.5, 8.],
            [8., 10.],
            [10., 12.],
            [12., 14.],
            [14., 16.],
            [16., 17.5]])

        super(self.__class__, self).__init__(dN = dN, bins = bins, **kwargs)

    def __repr__(self):
        return "Alphasense OPC-N2"
