"""Gender of a first name in a country, like genderize.io."""

import json
import re
from importlib.resources import files

from . import dictionary

COUNTRIES = json.loads(files(__package__).joinpath("country_iso2.json").read_text(encoding="utf-8"))

_table = None


def table():
    """The dictionary, loaded on first use."""
    global _table
    if _table is None:
        _table = dictionary.load()
    return _table


def use_table(t):
    """Use another dictionary (`dictionary.load(path)` or a dict of the same shape), e.g. in tests."""
    global _table
    _table = t


def country_code(country):
    """ISO2 code for an ISO2 code or a country name (INSPIRE/English spelling); '' if unknown."""
    if not country:
        return ""
    c = country.strip()
    if len(c) == 2 and c.isalpha():
        return c.upper()
    return COUNTRIES.get(c) or COUNTRIES.get(c.lower(), "")


def tokens(names):
    """Lowercase given names, without initials, punctuation or hyphens."""
    names = re.sub(r'[|†•()"]', " ", names or "").replace("-", " ").replace(".", " ")
    return [t.lower() for t in names.split() if len(t) > 1]


def p_female(name, country=""):
    """(share of women, countries listing the name) for one name, or None if it is not in the dictionary."""
    t = table()
    e = t.get(name) or t.get(dictionary.strip_accents(name))
    if not e:
        return None
    world, n, extra = e
    code = country_code(country)
    if code and code + ":" in extra:
        for item in extra.split(","):
            c, p = item.split(":")
            if c == code:
                return float(p), n
    return world, n


def guess(names, country=""):
    """(gender, probability, count) for given names and a country (ISO2 or name).

    The first given name found in the dictionary decides. gender is 'male',
    'female' or 'unknown'; probability is 0.5-1 (0 for unknown); count is the
    number of countries listing the name.
    """
    for tok in tokens(names):
        r = p_female(tok, country)
        if r is None:
            continue
        pf, n = r
        if pf == 0.5:
            return "unknown", 0.0, n
        return ("female", round(pf, 2), n) if pf > 0.5 else ("male", round(1 - pf, 2), n)
    return "unknown", 0.0, 0


def genderize(names, country_id=None):
    """Answer shaped like genderize.io's: {name, gender, probability, count, country_id}.

    gender is None when unknown, as in genderize.io.
    """
    g, p, n = guess(names, country_id or "")
    out = {"count": n, "name": names, "gender": None if g == "unknown" else g, "probability": p}
    if country_id:
        out["country_id"] = country_id
    return out
