"""
Loaders:
  1. SMPS
  2. Alphasense
        a. Just return histogram data from either a single file or a group of files?
"""

import glob
import os
import warnings
import pandas as pd
import numpy as np
import math
from .errors import DataFormatError, LoaderError

SMPS_META_COLUMN_NAMES = [
    'Classifier Model',
    'DMA Model',
    'DMA Inner Radius',
    'DMA Outer Radius',
    'DMA Characteristic Length',
    'CPC Model',
    'Gas Viscocity',
    'Mean Free Path',
    'Channels Per Decade',
    'Multiple Charge Correction',
    'Nanoparticle Aggregate Mobility Analysis',
    'Diffusion Correction',
    'Units'
]

SMPS_COLUMN_NAMES = [
    'Scan Up Time',
    'Retrace Time',
    'Down Scan First',
    'Scans Per Sample',
    'Impactor Type',
    'Sheath Flow',
    'Aerosol Flow',
    'CPC Inlet Flow',
    'CPC Sample Flow',
    'Low Voltage',
    'High Voltage',
    'Lower Size',
    'Upper Size',
    'Density',
    'Title',
    'Status Flag',
    'td',
    'tf',
    'D50',
    'Median',
    'Mean',
    'Geo. Mean',
    'Mode',
    'Geo Std Dev',
    'Total Concentration',
    'Comment'
]

class AlphasenseLoader(object):
    def __init__(self, **kwargs):
        self.dir    = None
        self.data   = None
        self.hist   = None

    def load(self, dir, kw = "*.csv", **kwargs):
        """Load the files into the data variable as a pd.DataFrame
        """
        data = []

        self.dir = dir

        # Get the files
        files = glob.glob(os.path.join(self.dir, kw))

        # Concatenate the files
        for each in files:
            df = pd.read_csv(each, parse_dates = True, index_col = 0, **kwargs)

            data.append(df)

        # Set the data attribute to the pd.DataFrame
        self.data = pd.concat(data)
        self.hist = self.histogram()

        return

    def histogram(self):
        """Return just the histogram information from the pd.DataFrame
        """
        if self.data is None:
            raise DataFormatError("You must load your data before accessing it!")

        bins = ['bin{}'.format(i) for i in range(16)]

        return self.data[bins]

class SMPS(object):
    """Loader for SMPS data in either dN or dNdlogDp format. If it is in dNdlogDp format,
    it will be converted using the SMPS multiplier.
    """
    def __init__(self, **kwargs):
        self.data       = pd.DataFrame()
        self.meta       = {}

        self.delimiter          = kwargs.get('delimiter', ',')
        self.encoding           = kwargs.get('encoding', 'ISO-8859-1')
        self.multiplier         = kwargs.get('multiplier', 64.)
        self.header             = kwargs.get('header', None)
        self.index_col          = kwargs.get('index_col', 0)
        self.bins               = None
        self.bin_names          = None

        # Make sure the multiplier is valid
        assert self.multiplier in [64, 32, 16, 8, 4], "Invalid multiplier"

    def load(self, path, **kwargs):
        """Load a file and save the data as internal variables
        """

        midpoint_method    = kwargs.get('midpoint_method', 'Inherit')

        meta         = pd.read_table(path,
                                     nrows = 13,
                                     skiprows = 1,
                                     delimiter = self.delimiter,
                                     header = None,
                                     encoding = self.encoding,
                                     index_col = 0).T

        meta.columns = SMPS_META_COLUMN_NAMES
        self.meta    = meta.ix[1, :].to_dict()

        # Read in the rows that contain the timestamp information
        ts         = pd.read_table(path, nrows = 2, skiprows = 15, delimiter = self.delimiter, encoding = self.encoding).ix[:, 1:].T
        ts.columns = ['Date', 'Time']

        # Read in the rest of the data
        tmp = pd.read_table(path,
                            skiprows = 19,
                            delimiter = self.delimiter,
                            header = None,
                            warn_bad_lines = True,
                            encoding = self.encoding)

        _bin_count      = self._get_bin_count(path)

        BIN_NAMES       = ["Bin {}".format(i) for i in range(_bin_count)]

        self.histogram  = tmp.ix[:_bin_count - 1, 1:].T.astype(float)
        _df_2           = tmp.ix[_bin_count:, 1:].T

        # If the meta information says tha the format is dw/dlogDp, convert to dN
        if self.meta['Units'] == 'dw/dlogDp':
            self.histogram = self.histogram.div(float(self.multiplier))

        self.histogram.columns  = BIN_NAMES
        _df_2.columns           = SMPS_COLUMN_NAMES

        # Try converting columns to float
        for col in SMPS_COLUMN_NAMES:
            try:
                _df_2[col] = _df_2[col].astype(float)
            except:
                pass

        self.data               = pd.merge(self.histogram, _df_2, left_index = True, right_index = True, how = 'outer')
        self.data.index         = ts.apply(lambda x: pd.to_datetime("{} {}".format(x['Date'], x['Time'])), axis = 1)
        self.histogram.index    = self.data.index

        # Create a DataFrame for other sizing information
        self.bins       = np.empty([_bin_count, 3])

        self.bins.fill(np.NaN)

        self.bins[0, 0]     = float(self.data.ix[0, 'Lower Size'])
        self.bins[-1, -1]   = float(self.data.ix[0, 'Upper Size'])
        self.bins[:, 1]     = tmp.ix[:_bin_count - 1, 0]

        #if midpoint_method == 'Inherit':
        #    self.bins[:, 1] = tmp.ix[:_bin_count - 1, 0]

        for i in range(self.bins.shape[0] - 1):
            self.bins[i, 2]     = round(math.pow(10, np.log10(self.bins[i, 0]) + (1 / self.multiplier)), 4)
            self.bins[i + 1, 0] = self.bins[i, 2]

            # Bin Midpoint Calculations
            #if midpoint_method == 'LM':
            #    self.bins[i, 1] = np.exp(0.5 * (np.log(self.bins[i, 0]) + np.log(self.bins[i, 2])))
            #elif midpoint_method == 'Mean':
            #    self.bins[i, 1] = np.mean([self.bins[i, 0], self.bins[i, 2]])
            #else:
            #    pass

        # Convert from nm to um
        self.bins = self.bins / 1000.

        return

    def _get_bin_count(self, file):
        """Get the number of bins in the file
        """
        bins = 0

        with open(file, 'r', encoding = self.encoding) as f:
            for line in f:
                try:
                    if float(line.split(',')[0]):
                        bins = bins + 1
                except: pass

        return bins
