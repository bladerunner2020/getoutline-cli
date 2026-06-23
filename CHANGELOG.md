# Changelog

## 0.5.0 (2026-06-24)

### Added

- Global substitutions at the top level of config, applied to all documents before per-document substitutions.
- `--version` flag to print the version and exit.
- Print version on startup.
- Automatic resolution of internal links: markdown links to files listed in config are replaced with their Outline URLs.
- Transliteration of Cyrillic anchor fragments (e.g. `#часовой-пояс` → `#h-chasovoj-poyas`).

## 0.4.2 (2025-01-12)

### Fixed

- Updated README.md with correct installation and usage instructions.

## 0.4.0 (2025-01-12)

### Added

- Preview option to display document without publishing.

### Fixed

- Fixed `OUTLINE_URL` environment variable description.

## 0.3.0 (2025-01-12)

### Added

- Ability to specify token and URL via environment variables `OUTLINE_API_TOKEN` and `OUTLINE_URL`.

## 0.2.0 (2023-01-11)

### Added

- Initial release of `getoutline-cli` with the following features:
  - Publish markdown files to Outline wiki.
  - Support for configuration file `.outline-cli.yml`.
  - Support for text substitutions using regular expressions.
