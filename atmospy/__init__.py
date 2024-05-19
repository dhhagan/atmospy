from importlib.metadata import version

# import warnings
# import pandas as pd
# import numpy as np
# import math
# import os

from .utils import *
from .rcmod import *
from .relational import *
from .trends import *
from .rose import *
from .stats import *

# Capture the original matplotlib rcParams
import matplotlib as mpl
_orig_rc_params = mpl.rcParams.copy()

# Determine the atmospy version
__version__ = version('atmospy')
