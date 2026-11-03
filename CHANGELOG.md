# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-03

### Added

- `guess(names, country)` and `genderize(names, country_id)` (genderize.io-shaped answer),
  `country_code`, `tokens`, `p_female`.
- Command `genderize-offline` with `name`, `csv`, `fetch` and `build`.
- Compact dictionary built from WGND 2.0, published as the GitHub release `wgnd-2.0-r1`
  and downloaded on first use with a SHA-256 check; fallback build from Harvard Dataverse.
- Benchmarks against genderize.io (`benchmarks/benchmark.py`, README).

[Unreleased]: https://github.com/restrepo/genderize-offline/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/restrepo/genderize-offline/releases/tag/v0.1.0
