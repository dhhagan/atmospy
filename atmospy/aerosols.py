from .errors import DataFormatError

import pandas as pd
import numpy as np
import warnings
import math

class ParticleDistribution(object):
    """Generic Particle Distribution

    - Histogram should be a pd.DataFrame
    - bins should be a 3d array (in microns)

    """
    def __init__(self, histogram, bins, **kwargs):
        self.raw        = histogram
        self.bins       = bins
        self.density    = kwargs.pop('density', 1.65)
        self.data       = None
        self.stats      = None

        assert isinstance(self.raw, pd.DataFrame), "`histogram` must be a pandas.DataFrame"
        assert isinstance(self.bins, np.ndarray), "`bins` must be a numpy.ndarray"
        assert self.bins.shape[1] == 3, "`bins` must be a 3xn numpy.ndarray"
        assert self.bins.shape[0] == self.raw.shape[1], \
            "The `bins` array must account for all columns in the histogram"

        # Rename the index
        self.raw.index.rename('index', inplace = True)
        self.raw.replace(0, np.nan).dropna(how = 'all', inplace = True)
        self.raw = self.raw.reset_index().drop_duplicates('index').set_index('index')

        self.meta = pd.DataFrame.from_dict({
            'bin_left': self.bins[:, 0],
            'Dp': self.bins[:, 1],
            'bin_right': self.bins[:, 2]
            })

        self.meta['logDp']  = self.meta['Dp'].apply(np.log10)
        self.meta['dDp']    = self.meta['bin_right'] - self.meta['bin_left']
        self.meta['dlogDp'] = self.meta.apply(lambda x: np.log10(x['bin_right']) - np.log10(x['bin_left']) , axis = 1)

    def compute(self, **kwargs):
        """Perform all calculations and set the panel data
        """
        dN  = self.raw
        dD  = dN.mul(self.meta['Dp'].values)
        dS  = dN.mul((self.meta['Dp'] ** 2 * math.pi).values)
        dV  = dN.mul((self.meta['Dp'] ** 3 * math.pi / 6.).values)

        dNdDp   = dN.div(self.meta['dDp'].values) # [um-1 cm-3], S+P 8.3
        dSdDp   = dS.div(self.meta['dDp'].values) # [um cm-3], S+P 8.4
        dVdDp   = dV.div(self.meta['dDp'].values) # [um2 cm-3], S+P 8.6

        dNdlogDp    = dNdDp.mul(2.3025).mul(self.meta['Dp'].values) # S+P 8.18
        dSdlogDp    = dSdDp.mul(2.3025).mul(self.meta['Dp'].values) # S+P 8.19
        dVdlogDp    = dVdDp.mul(2.3025).mul(self.meta['Dp'].values) # S+P 8.20

        self.data = pd.Panel({
            'dN': dN,
            'dD': dD,
            'dS': dS,
            'dV': dV,
            'dNdDp': dNdDp,
            'dSdDp': dSdDp,
            'dVdDp': dVdDp,
            'dNdlogDp': dNdlogDp,
            'dSdlogDp': dSdlogDp,
            'dVdlogDp': dVdlogDp
            })

        return

    def statistics(self):
        """
        """
        num     = pd.DataFrame({ 'N Total': self.data['dN'].sum(axis = 1) })
        diam    = pd.DataFrame({ 'N Total': self.data['dD'].sum(axis = 1) })
        sa      = pd.DataFrame({ 'N Total': self.data['dS'].sum(axis = 1) })
        vol     = pd.DataFrame({ 'N Total': self.data['dV'].sum(axis = 1) })

        num['Mean']     = 1000. * self.data['dN'].mul(self.meta['Dp'].values).sum(axis = 1) / num['N Total']    # [nm]
        diam['Mean']    = 1000. * self.data['dD'].mul(self.meta['Dp'].values).sum(axis = 1) / diam['N Total']   # [nm]
        sa['Mean']      = 1000. * self.data['dS'].mul(self.meta['Dp'].values).sum(axis = 1) / sa['N Total']     # [nm]
        vol['Mean']     = 1000. * self.data['dV'].mul(self.meta['Dp'].values).sum(axis = 1) / vol['N Total']    # [nm]

        num['GM']   = 1000. * np.exp(self.data['dN'].mul(np.log(self.meta['Dp'].values)).sum(axis = 1) / num['N Total'])   # [nm]
        diam['GM']  = 1000. * np.exp(self.data['dD'].mul(np.log(self.meta['Dp'].values)).sum(axis = 1) / diam['N Total'])  # [nm]
        sa['GM']    = 1000. * np.exp(self.data['dS'].mul(np.log(self.meta['Dp'].values)).sum(axis = 1) / sa['N Total'])    # [nm]
        vol['GM']   = 1000. * np.exp(self.data['dV'].mul(np.log(self.meta['Dp'].values)).sum(axis = 1) / vol['N Total'])   # [nm]

        for i, r in num.iterrows():
            num.loc[i, 'GSD'] = np.exp(np.sqrt((self.data['dN'].ix[i].values *  \
                    ((np.log(self.meta['Dp']) - np.log(r['GM'] / 1000.)) ** 2)).sum() / r['N Total']))

            diam.loc[i, 'GSD'] = np.exp(np.sqrt((self.data['dD'].ix[i].values * \
                    ((np.log(self.meta['Dp']) - np.log(diam.loc[i]['GM'] / 1000.)) ** 2)).sum() / diam.loc[i]['N Total']))

            sa.loc[i, 'GSD'] = np.exp(np.sqrt((self.data['dS'].ix[i].values * \
                    ((np.log(self.meta['Dp']) - np.log(sa.loc[i]['GM'] / 1000.)) ** 2)).sum() / sa.loc[i]['N Total']))

            vol.loc[i, 'GSD'] = np.exp(np.sqrt((self.data['dV'].ix[i].values * \
                    ((np.log(self.meta['Dp']) - np.log(vol.loc[i]['GM'] / 1000.)) ** 2)).sum() / vol.loc[i]['N Total']))

        self.stats = pd.Panel({
            'Number': num,
            'Diameter': diam,
            'Surface Area': sa,
            'Volume': vol
        })

        return

    def _bin_lookup(self, cutoff):
        '''Cutoff is in um
        '''
        return self.meta.query("{0} >= bin_left and {0} <= bin_right".format(cutoff)).index.tolist()[0]

"""
    def subset(self, cutoff = None):
        if cutoff is None:
            return self.dN

        # Locate the index of the bin that must be selected
        i = self.info.query("left < {}".format(cutoff)).index[-1]

        f = (cutoff - (self.info.loc[i]['left'])) / (self.info.loc[i]['right'] - self.info.loc[i]['left'])

        # Recalculate the Last bin and return just the subset dN
        d = self.data[:, 'bin0':'bin{}'.format(i), ['dN', 'dS', 'dV', 'dM']].copy()

        d.ix[:, 'bin{}'.format(i)] = d[:, 'bin{}'.format(i), :].mul(f)

        return d

    def statistics(self, dN):
        # Calculate the SA CMD using S&P 8.50 and 8.53
        stats['cmd_SA'] = stats.apply(lambda x: np.exp(np.log(x['cmd']) + 2 * np.log(x['gsd']) ** 2), axis = 1)
        stats['cmd_V']  = stats.apply(lambda x: np.exp(np.log(x['cmd']) + 3 * np.log(x['gsd']) ** 2), axis = 1)

        return stats
"""


class AlphasenseOPCN2(ParticleDistribution):
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

        super(self.__class__, self).__init__(histogram = dN, bins = bins, **kwargs)

    def __repr__(self):
        return "Alphasense OPC-N2"
