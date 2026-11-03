# genderize-offline

[![CI](https://github.com/restrepo/genderize-offline/actions/workflows/ci.yml/badge.svg)](https://github.com/restrepo/genderize-offline/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/genderize-offline.svg)](https://pypi.org/project/genderize-offline/)
[![Python](https://img.shields.io/pypi/pyversions/genderize-offline.svg)](https://pypi.org/project/genderize-offline/)

Offline gender inference from first names and country, a free drop-in for genderize.io, using the World Gender Name Dictionary 2.0.

## Install

```bash
pip install genderize-offline
genderize-offline --version
```

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check . && ruff format --check .
```

Releases are published to PyPI from GitHub Actions when a `v*` tag is pushed; see [PUBLISHING.md](PUBLISHING.md) and [CHANGELOG.md](CHANGELOG.md).
