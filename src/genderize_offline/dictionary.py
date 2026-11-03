"""The name dictionary: a compact table derived from WGND 2.0.

WGND 2.0 (World Gender Name Dictionary, Raffo 2021, Harvard Dataverse,
doi:10.7910/DVN/MSEGSJ, CC0) gives, for each (name, ISO2 country), the share
of women and men. The compact table keeps one line per name::

    name <TAB> p_female averaged over its countries <TAB> number of countries <TAB> CC:p,CC:p,...

where only countries whose share differs from the average are listed. It is
built with `build()` from the original CSV and published as a GitHub release
asset of this repository (tag `wgnd-2.0-rN`); `load()` downloads it once,
checks its SHA-256 and caches it.
"""

import bisect
import csv
import gzip
import hashlib
import os
import shutil
import tempfile
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

WGND_URL = "https://dataverse.harvard.edu/api/access/datafile/4750348?format=original"

DICTIONARY_RELEASE = "wgnd-2.0-r1"
DICTIONARY_FILE = "wgnd2_compact.tsv.gz"
DICTIONARY_URL = (
    f"https://github.com/restrepo/genderize-offline/releases/download/{DICTIONARY_RELEASE}/{DICTIONARY_FILE}"
)
DICTIONARY_SHA256 = "c9020732db57856a45f5bdb469b971a5ad3febf684eef0e6256757b61a07ffaf"


def cache_dir():
    """`$GENDERIZE_OFFLINE_CACHE`, else `~/.cache/genderize-offline`."""
    return Path(os.environ.get("GENDERIZE_OFFLINE_CACHE") or Path.home() / ".cache" / "genderize-offline")


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build(src_csv, dst_gz):
    """Write the compact table from WGND's `wgnd_2_0_name-gender-code.csv`. Returns the number of names."""
    raw = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    with open(src_csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["gender"] in ("F", "M"):
                raw[r["name"].strip().lower()][r["code"]][r["gender"] == "M"] += float(r["wgt"] or 0)
    rows = {}
    for name, by_code in raw.items():
        by = {c: fm[0] / (fm[0] + fm[1]) for c, fm in by_code.items() if fm[0] + fm[1] > 0}
        if not by or not name or "\t" in name or "\n" in name:
            continue
        world = round(sum(by.values()) / len(by), 6)
        extra = ",".join(f"{c}:{round(p, 6):g}" for c, p in sorted(by.items()) if c and round(p, 6) != world)
        rows[name] = f"{world:g}\t{sum(1 for c in by if c)}\t{extra}"
    # an accent-free spelling not in WGND gets the entry of the first accented one (andres -> andrés)
    for name in sorted(rows):
        rows.setdefault(strip_accents(name), rows[name])
    lines = sorted(f"{name}\t{v}" for name, v in rows.items())
    # mtime=0 so the same input gives the same bytes (and SHA-256)
    with open(dst_gz, "wb") as raw_out, gzip.GzipFile(filename="", fileobj=raw_out, mode="wb", mtime=0) as gz:
        gz.write(("\n".join(lines) + "\n").encode("utf-8"))
    return len(lines)


def download(url, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dst.parent, delete=False) as tmp, urllib.request.urlopen(url) as r:
        shutil.copyfileobj(r, tmp)
    os.replace(tmp.name, dst)


def fetch(from_wgnd=False):
    """Make sure the compact table is in the cache and return its path.

    By default it is downloaded from this repository's release and checked
    against `DICTIONARY_SHA256`; with `from_wgnd=True` (or if the release is
    unreachable) it is built from the original WGND CSV on Harvard Dataverse.
    """
    path = cache_dir() / DICTIONARY_FILE
    if path.exists() and (from_wgnd or sha256(path) == DICTIONARY_SHA256):
        return path
    if not from_wgnd:
        try:
            download(DICTIONARY_URL, path)
            if sha256(path) == DICTIONARY_SHA256:
                return path
            path.unlink()
        except OSError:
            pass
    src = cache_dir() / "wgnd_2_0_name-gender-code.csv"
    if not src.exists():
        download(WGND_URL, src)
    build(src, path)
    return path


class Table:
    """The compact table in memory: sorted lines, looked up by bisection."""

    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def get(self, name, default=None):
        key = name + "\t"
        i = bisect.bisect_left(self.lines, key)
        if i < len(self.lines) and self.lines[i].startswith(key):
            _, world, n, extra = self.lines[i].split("\t")
            return float(world), int(n), extra
        return default


def load(path=None):
    """The dictionary as a `Table`: `.get(name)` → (p_female world, n_countries, "CC:p,...") or None."""
    path = Path(path) if path else fetch()
    with open(path, "rb") as f:
        text = gzip.decompress(f.read()).decode("utf-8")
    return Table(text.splitlines())
