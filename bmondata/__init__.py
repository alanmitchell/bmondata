# The version number is stored in pyproject.toml, the single source of truth,
# and is read back here from the installed package metadata.  Bump it with
# `uv version --bump patch` (see PUBLISHING.md).
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('bmondata')
except PackageNotFoundError:
    # Running from a source tree where the package has not been installed.
    __version__ = 'unknown'

# Version info
# 1.0.7: Switched to uv version for version management. Added pytz and dateutil to dependencies.
# 1.0.6: Added handling of building or organization ID of 0
# 1.0.5: Added schedule module
# 1.0.3 & 1.0.4: Bad releases, had to delete.

# Classes and methods that are in the top-level namespace
from .server import Server

# Make all utility functions top-level
from .util import *

# Import Schedule class into this namespace
from .schedule import Schedule
