"""Command line entry point: `genderize-offline`."""

import argparse

from . import __version__


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="genderize-offline",
        description="Offline gender inference from first names and country, a free drop-in for genderize.io, using the World Gender Name Dictionary 2.0.",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
