# genderize-offline

[![CI](https://github.com/restrepo/genderize-offline/actions/workflows/ci.yml/badge.svg)](https://github.com/restrepo/genderize-offline/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/genderize-offline.svg)](https://pypi.org/project/genderize-offline/)
[![Python](https://img.shields.io/pypi/pyversions/genderize-offline.svg)](https://pypi.org/project/genderize-offline/)

Infer gender from first names and country **offline**: a free drop-in for
[genderize.io](https://genderize.io), with no API key, no quota and no network
after the first use. It uses the
[World Gender Name Dictionary 2.0](https://doi.org/10.7910/DVN/MSEGSJ) (WGND, Raffo 2021,
CC0), which gives the share of women and men for 4.9 million name–country pairs.
Standard library only.

## Install

```bash
pip install genderize-offline
genderize-offline fetch          # once: downloads the dictionary (14 MB) into the cache
```

## Use

```python
from genderize_offline import guess, genderize

guess("Natalia Andrea", "CO")      # ('female', 1.0, 58)
guess("Andrea", "Italy")           # ('male', 1.0, 77)  country names or ISO2 codes
guess("Andrea", "CO")              # ('female', 0.96, 77)
genderize("Andrea", "IT")          # {'count': 77, 'name': 'Andrea', 'gender': 'male', 'probability': 1.0, 'country_id': 'IT'}
```

`guess(names, country)` returns `(gender, probability, count)`: gender `male`, `female` or
`unknown`; probability 0.5–1 (0 for unknown); count, the number of countries that list the
name (genderize.io's count is people). `genderize()` answers in genderize.io's shape, with
`gender` `None` when unknown. As with genderize.io, set your own threshold: the benchmarks
below count a gender only at probability ≥ 0.9.

```bash
genderize-offline name "María José" ES
genderize-offline csv authors.csv out.csv --name-col first_names --country-col country
```

### Method

- Names are lowercased and split on spaces, hyphens and dots; initials are dropped.
- The first given name found in the dictionary decides (genderize.io also uses the first word).
- The share of women is WGND's for that name in the given country; if the country is missing
  or doesn't list the name, the average over every country that lists it is used.
- Accents are optional: `andres` finds `andrés`, `josé` finds `jose`.

## Benchmarks

Run with `python benchmarks/benchmark.py LABELLED.csv [AUTHORS.json]` (threshold 0.9). The inputs
hold names of real people and are not in this repository; they are files of
[restrepo/inspireauth](https://github.com/restrepo/inspireauth).

**Hand-labelled names** (`data/test_gender.csv`: 3,965 names, 3,820 of them Colombian, with
their true gender and genderize.io's answer):

| | genderize.io | genderize-offline |
|---|---|---|
| Names given a gender (coverage) | 98.1% | 93.6% |
| Accuracy where a gender is given | 99.38% | 98.98% |

**INSPIRE-HEP authors with Latin American affiliations** (`data/inspire_LA.json`: 29,979
physicists, genders from genderize.io):

| genderize.io ↓ / offline → | male | female | unknown |
|---|---|---|---|
| male | 14,485 | 39 | 680 |
| female | 23 | 2,635 | 155 |
| unknown | 677 | 176 | 11,109 |

| | genderize.io | genderize-offline |
|---|---|---|
| Authors with a gender | 18,017 | 18,035 |
| Female share | 15.6% | 15.8% |

Where both give a gender (17,182 authors) they agree on **99.64%**.

**Effect on published results.** We recomputed the female fractions of *Statistical Analysis
of Scientific Metrics in High Energy, Cosmology, and Astroparticle Physics in Latin America*
(Morales-Alvarado, Quevedo, Ramos-Hamud, Restrepo) with offline genders. Every value moves
by less than its 95% margin:

| Female share by rank (Table 8) | genderize.io | offline |
|---|---|---|
| All ranks | 11.9% | 12.3% |
| Undergraduate, Master, PhD | 14.3% | 14.7% |
| Postdoc | 13.4% | 14.0% |
| Junior or Staff | 12.6% | 12.2% |
| Senior | 7.9% | 8.5% |

The female share per year (Fig. 21, 45 years with at least 100 authors) differs by −0.04
points on average and by at most 1.2 points.

**Speed** (one core, laptop): the dictionary loads in about 1 s; lookups run at about
140,000 names/s.

The genders are estimates from names, not self-reported gender. Report them as such, and
cite WGND 2.0 (Raffo, J. (2021). WGND 2.0. Harvard Dataverse. doi:10.7910/DVN/MSEGSJ).

## The dictionary and this repository

The 91 MB WGND CSV is not stored in git. Instead:

1. **Built reproducibly.** `genderize-offline build wgnd.csv wgnd2_compact.tsv.gz` turns
   WGND's `wgnd_2_0_name-gender-code.csv` into a compact table (one sorted line per name: average
   share of women, number of countries, and the countries that differ from the average). The
   same input gives the same bytes, so anyone can check the SHA-256.
2. **Published as a release asset.** The manual workflow [Dictionary](.github/workflows/dictionary.yml)
   downloads WGND from Harvard Dataverse, builds the table and attaches it with its
   `SHA256SUMS` to a GitHub release of its own, `wgnd-2.0-rN`. These tags don't start
   with `v`, so they never publish to PyPI, and they aren't marked latest.
3. **Pinned in the code.** `dictionary.py` names the release and the SHA-256. On first use,
   `fetch()` downloads the file to `~/.cache/genderize-offline/` (or `$GENDERIZE_OFFLINE_CACHE`)
   and refuses it if the hash differs. If the release can't be reached, it builds the table
   from Dataverse instead (`genderize-offline fetch --from-wgnd`).

To change the dictionary (a new WGND version or a new build rule), run the workflow with the
next tag, update `DICTIONARY_RELEASE` and `DICTIONARY_SHA256`, and release a new version.
Old releases keep their assets, so older package versions keep working.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check . && ruff format --check .
```

Tests use a synthetic dictionary and need no network. Releases are published to PyPI from
GitHub Actions when a `v*` tag is pushed; see [PUBLISHING.md](PUBLISHING.md) and
[CHANGELOG.md](CHANGELOG.md).

## License

Code: MIT. Dictionary: derived from WGND 2.0, CC0 1.0.
