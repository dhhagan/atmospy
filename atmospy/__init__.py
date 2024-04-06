from pkg_resources import get_distribution

# import warnings
# import pandas as pd
# import numpy as np
# import math
# import os

from .utils import *
from .calendar import *
from .relational import *
from .trends import *

# Capture the original matplotlib rcParams
import matplotlib as mpl
_orig_rc_params = mpl.rcParams.copy()

# Determine the atmospy version
__version__ = get_distribution('atmospy').version
