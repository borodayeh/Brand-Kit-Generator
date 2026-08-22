# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [3.0.0] - 2026-08-22

### Added
- **Templates:** `full` (55 folders), `minimal`, `startup` and `agency`,
  selectable with `--template`; `--list-templates` shows them all.
- **Brand placeholder:** `--brand "Acme"` substitutes `{brand}` in folder
  names, titles and descriptions.
- **`MANIFEST.md`:** a bilingual overview of the whole generated tree
  (disable with `--no-manifest`).
- **`--zip`:** package the result into a ZIP archive.
- **`--git-init`:** initialise a git repository in the destination with a
  `.gitattributes` that tracks binary assets through Git LFS.
- **Web interface:** `brandkit --web` starts a dependency-free, bilingual
  (RTL-aware) local UI with a live tree preview and ZIP download.
- **JSON Schema** (`structure.schema.json`) plus
  `scripts/validate_templates.py`.
- **Test suite:** 95 pytest cases covering sanitisation, traversal, templates,
  rendering, CLI behaviour and the web app.
- **Packaging:** `pyproject.toml`, the `brandkit` console script and
  `python -m brand_kit_generator`.
- **Project infrastructure:** MIT `LICENSE`, GitHub Actions CI (Linux/Windows/
  macOS × Python 3.9–3.13), PyPI publish workflow, `CONTRIBUTING.md`,
  `.editorconfig`, issue templates.

### Changed
- The implementation moved into the `brand_kit_generator` package;
  `create_brand_kit.py` remains as a working compatibility shim.
- `structure.json` became `brand_kit_generator/templates/full.json`.

## [2.0.0] - 2026-08-22

### Added
- Full `argparse` CLI: `--structure`, `--lang`, `--force`, `--dry-run`,
  `--no-samples`, `--verbose`, `--quiet`, `--version`.
- Bilingual message layer with automatic language detection from
  `BRANDKIT_LANG` / `LC_ALL` / `LC_MESSAGES` / `LANG`.
- `title_en` / `title_fa` display names on all 55 nodes.
- Structure validation: unknown keys, wrong types, case-insensitive
  collisions.
- Windows hardening: reserved device names, trailing dots and spaces,
  long-path warnings, UTF-8 stdio.
- Summary report with created / existing / written / skipped / error counts.

### Fixed
- `structure.json` is resolved relative to the script, not the working
  directory — the script now runs from anywhere.
- Existing files are never overwritten without `--force` (previously silent
  data loss on re-runs).
- Path traversal: `../`, absolute paths and separators inside node names can
  no longer write outside the destination.
- `~` and environment variables in the destination path are expanded.
- Meaningful exit codes (`0`, `1`, `2`, `130`) instead of always `0`.
- `EOFError` / `KeyboardInterrupt` are handled gracefully.
- Per-node errors are collected and reported instead of printing a false
  success message.

### Changed
- Generated Persian content is wrapped in `<div dir="rtl">`.
- Documentation split into `README.md` (English) and `README.fa.md` (Persian).

## [1.0.0]

- Initial release: recursive folder creation from `structure.json` with a
  bilingual `README.md` in every folder.
