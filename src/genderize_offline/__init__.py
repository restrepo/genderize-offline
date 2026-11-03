"""Offline gender inference from first names and country, a free drop-in for genderize.io, using the World Gender Name Dictionary 2.0."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("genderize-offline")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0"

__all__ = ["__version__"]
