"""Command line entry point: `genderize-offline`."""

import argparse
import csv
import json
import sys

from . import __version__, dictionary
from .core import guess


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="genderize-offline",
        description="Offline gender inference from first names and country, a free drop-in for genderize.io, "
        "using the World Gender Name Dictionary 2.0.",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("name", help="gender of one name, as JSON")
    p.add_argument("names")
    p.add_argument("country", nargs="?", default="", help="ISO2 code or country name")
    p = sub.add_parser("csv", help="add gender columns to a CSV")
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--name-col", default="name")
    p.add_argument("--country-col", default="country_id")
    p.add_argument("--prefix", default="", help="prefix of the added columns gender, probability, count")
    p = sub.add_parser("fetch", help="download the dictionary into the cache")
    p.add_argument("--from-wgnd", action="store_true", help="build it from the original WGND CSV instead")
    p = sub.add_parser("build", help="build the compact dictionary from WGND's name-gender-code CSV")
    p.add_argument("src")
    p.add_argument("dst")
    a = ap.parse_args(argv)

    if a.cmd == "name":
        g, p_, n = guess(a.names, a.country)
        print(json.dumps({"name": a.names, "gender": g, "probability": p_, "count": n}, ensure_ascii=False))
    elif a.cmd == "csv":
        with open(a.src, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cols = [f"{a.prefix}gender", f"{a.prefix}probability", f"{a.prefix}count"]
        with open(a.dst, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(rows[0]) + cols if rows else cols)
            w.writeheader()
            for r in rows:
                r.update(zip(cols, guess(r.get(a.name_col, ""), r.get(a.country_col, "")), strict=True))
                w.writerow(r)
    elif a.cmd == "fetch":
        print(dictionary.fetch(from_wgnd=a.from_wgnd))
    elif a.cmd == "build":
        n = dictionary.build(a.src, a.dst)
        print(f"{a.dst}: {n} names, sha256 {dictionary.sha256(a.dst)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
