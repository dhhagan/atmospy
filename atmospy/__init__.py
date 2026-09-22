from importlib.metadata import version as _version

from .utils import *
from .rcmod import *
from .relational import *
from .trends import *
from .rose import *
from .stats import *

# Determine the atmospy version
__version__ = _version("atmospy")
