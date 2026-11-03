"""Offline gender inference from first names and country, a free drop-in for genderize.io (WGND 2.0)."""

from importlib.metadata import PackageNotFoundError, version

from .core import country_code, genderize, guess, p_female, tokens, use_table

try:
    __version__ = version("genderize-offline")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0"

__all__ = ["__version__", "country_code", "genderize", "guess", "p_female", "tokens", "use_table"]
