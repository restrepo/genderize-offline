"""Benchmarks of genderize-offline against genderize.io (numbers in README.md).

Usage: python benchmarks/benchmark.py LABELLED.csv [AUTHORS.json] [--threshold 0.9]

LABELLED.csv: hand-labelled names with columns names, gender (the true one),
country_id, and genderize.io's answer in Gender and Gender Probability
(as `data/test_gender.csv` of restrepo/inspireauth).
AUTHORS.json: records with first_names, country, author_id and genderize.io's
gender and gender_probability (as `data/inspire_LA.json` of restrepo/inspireauth).
"""

import argparse
import csv
import json
import time
from collections import Counter

from genderize_offline import core, dictionary, guess


def scores(rows, thr):
    known = [(t, g) for t, g, p in rows if g in ("male", "female") and p >= thr]
    ok = sum(t == g for t, g in known)
    return f"coverage {100 * len(known) / len(rows):.1f}%, accuracy {100 * ok / len(known):.2f}% ({len(known)} names)"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("labelled")
    ap.add_argument("authors", nargs="?")
    ap.add_argument("--threshold", type=float, default=0.9)
    a = ap.parse_args(argv)
    thr = a.threshold

    t0 = time.perf_counter()
    core.use_table(dictionary.load())
    print(f"load: {time.perf_counter() - t0:.1f} s, {len(core.table())} names and aliases")

    with open(a.labelled, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    gz = [(r["gender"], r["Gender"] or "unknown", float(r["Gender Probability"] or 0)) for r in rows]
    t0 = time.perf_counter()
    og = [(r["gender"], *guess(r["names"], r["country_id"])[:2]) for r in rows]
    dt = time.perf_counter() - t0
    print(f"\nhand-labelled names: {len(rows)}, threshold {thr}  ({len(rows) / dt:,.0f} names/s)")
    print(f"  genderize.io      {scores(gz, thr)}")
    print(f"  genderize-offline {scores(og, thr)}")

    if not a.authors:
        return 0
    with open(a.authors, encoding="utf-8") as f:
        records = json.load(f)
    first = {}
    for r in records:
        first.setdefault(r["author_id"], r)
    pairs = Counter()
    for r in first.values():
        g0 = r["gender"] if r["gender_probability"] >= thr else "unknown"
        g, p, _ = guess(r.get("first_names", ""), r.get("country", ""))
        pairs[g0, g if p >= thr else "unknown"] += 1
    ks = ["male", "female", "unknown"]
    print(f"\nauthors: {len(first)}; rows genderize.io, columns genderize-offline")
    print(" " * 10 + "".join(f"{k:>10}" for k in ks))
    for x in ks:
        print(f"{x:>10}" + "".join(f"{pairs[x, y]:>10}" for y in ks))
    both = sum(pairs[x, y] for x in ks[:2] for y in ks[:2])
    agree = pairs["male", "male"] + pairs["female", "female"]
    print(f"agreement where both give a gender: {100 * agree / both:.2f}% of {both}")
    for name, i in [("genderize.io", 0), ("genderize-offline", 1)]:
        fe = sum(v for k, v in pairs.items() if k[i] == "female")
        ma = sum(v for k, v in pairs.items() if k[i] == "male")
        print(f"  {name:18s} {fe + ma} with a gender, female {100 * fe / (fe + ma):.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
