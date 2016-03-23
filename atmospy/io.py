"""
Loaders:
  1. SMPS
  2. Alphasense
        a. Just return histogram data from either a single file or a group of files?
"""

import glob
import os
import pandas as pd
from .errors import DataFormatError

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
