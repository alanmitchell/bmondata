__version__ = '1.0.3'
# Version info
# 1.0.3:  added schedule module

# Classes and methods that are in the top-level namespace
from .server import Server

# Make all utility functions top-level
from .util import *

# Import Schedule class into this namespace
from .schedule import Schedule