# Brand Kit Generator

[![CI](https://github.com/borodayeh/Brand-Kit-Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/borodayeh/Brand-Kit-Generator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**English** · [فارسی](README.fa.md)

A dependency-free Python tool that generates a complete, professional brand-kit
folder structure — with a bilingual (Persian/English) `README.md` inside every
folder, a CLI, and an optional local web interface.

```bash
brandkit ./MyBrand --brand Acme --template startup --lang fa --zip
```

---

## Features

- **Four built-in templates** — `full` (55 folders, agency grade), `minimal`, `startup`, `agency`.
- **Declarative** — the whole tree lives in JSON; no code changes needed to customise it.
- **Truly bilingual** — the generated documentation *and* the CLI itself speak Persian and English. Persian text is wrapped in `<div dir="rtl">` so it renders correctly right-to-left.
- **Brand aware** — `--brand "Acme"` substitutes `{brand}` in folder names, titles and descriptions.
- **Safe by default** — existing files are never overwritten unless you pass `--force`.
- **Sandboxed paths** — folder names are sanitised and validated; a malformed or malicious structure file can never write outside the destination.
- **Cross-platform** — Windows-illegal characters, reserved device names, trailing dots/spaces and long-path risks are all handled. CI runs on Linux, Windows and macOS.
- **Extras** — `MANIFEST.md` overview, `--zip` archive, `--git-init` with Git LFS rules.
- **Web UI** — `brandkit --web` opens a bilingual, RTL-aware page with a live tree preview and ZIP download. Still zero dependencies.
- **Tested** — 95 pytest cases, ruff, mypy and JSON-Schema validation in CI.

---

## Installation

```bash
pip install brand-kit-generator     # once published to PyPI
```

Or straight from the repository:

```bash
git clone https://github.com/borodayeh/Brand-Kit-Generator.git
cd Brand-Kit-Generator
pip install .
```

No installation at all? The script still works standalone:

```bash
python create_brand_kit.py ./MyBrand
```

Requires **Python 3.9+** and no third-party packages.

---

## Usage

```bash
# Interactive: asks for the destination
brandkit

# Direct
brandkit ./MyBrand

# A startup kit for "Acme", Persian only, zipped
brandkit ./MyBrand --brand Acme --template startup --lang fa --zip

# Preview without writing anything
brandkit ./MyBrand --dry-run --verbose

# Custom structure, no placeholder assets, no manifest
brandkit ./MyBrand --structure my_structure.json --no-samples --no-manifest

# Hand-off ready: git repo with LFS rules for binary assets
brandkit ./ClientKit --template agency --brand Contoso --git-init

# List the built-in templates
brandkit --list-templates

# Local web interface on http://localhost:8000
brandkit --web
```

Equivalent invocations: `brandkit …`, `python -m brand_kit_generator …`,
`python create_brand_kit.py …`. The tool can be run from **any** working
directory.

### Options

| Option | Description |
|---|---|
| `path` | Destination directory (prompted if omitted). `~` and `$VARS` are expanded. |
| `-t`, `--template NAME` | Built-in template: `full` (default), `minimal`, `startup`, `agency`. |
| `-s`, `--structure FILE` | Custom structure JSON (overrides `--template`). |
| `-b`, `--brand NAME` | Value substituted for `{brand}`. |
| `-l`, `--lang {fa,en,both}` | Language of the generated docs and the CLI. Default: auto-detected. |
| `-f`, `--force` | Overwrite files that already exist. |
| `-n`, `--dry-run` | Show what would be created without touching the disk. |
| `--no-samples` | Skip placeholder asset files. |
| `--no-manifest` | Skip `MANIFEST.md`. |
| `-z`, `--zip [FILE]` | Also create a ZIP archive (name defaults to `<brand>_brand_kit.zip`). |
| `--git-init` | `git init` the destination and add Git LFS rules for binary assets. |
| `--list-templates` | List the built-in templates and exit. |
| `--web` | Start the local web interface (`--host`, `--port`). |
| `-v`, `--verbose` / `-q`, `--quiet` | More / less output. |
| `-V`, `--version` | Show the version. |

### Language detection

When `--lang` is not given, the language is taken from the first of
`BRANDKIT_LANG`, `LC_ALL`, `LC_MESSAGES`, `LANG` that is set. Anything that is
not clearly Persian or English falls back to **bilingual** output.

```bash
BRANDKIT_LANG=fa brandkit ./MyBrand
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Finished, but one or more nodes failed |
| `2` | Invalid input (unknown template, missing/invalid structure file, empty path) |
| `130` | Cancelled by the user (Ctrl-C or closed stdin) |

---

## Templates

| Name | Folders | For |
|---|---|---|
| `full` | 55 | Agency-grade, covers legal, strategy, visual, motion, audio, templates, guidelines, archive |
| `minimal` | 5 | Freelancers and small teams |
| `startup` | 15 | Product-focused: brand basics, product UI, go-to-market, legal |
| `agency` | 19 | Client hand-off: discovery, concepts, final identity, production files |

```
Ultimate_Brand_Kit/                      (template: full)
├── 00_Legal_&_Licensing/
├── 01_Brand_Strategy_&_Verbal_Identity/
├── 02_Visual_Identity_Core/
│   ├── 01_Logos/            (primary, secondary, lockups, favicons, …)
│   ├── 02_Color_Palettes/
│   ├── 03_Typography/
│   └── 04_Visual_System/
├── 03_Motion_&_Audio_Identity/
├── 04_Templates_&_Assets/
├── 05_Brand_Guidelines/
└── 06_Archive_&_Historical_Data/
```

Example of a generated `README.md`:

```markdown
# Primary Logo / لوگوی اصلی

## English

**Primary Logo**

The main and primary version of the logo.

---

<div dir="rtl">

## فارسی

**لوگوی اصلی**

نسخه اصلی و اولیه لوگو.

</div>
```

---

## Web interface

```bash
brandkit --web                      # http://127.0.0.1:8000
brandkit --web --host 0.0.0.0 --port 3000
```

Pick a brand name, template and language, watch the folder tree update live,
then download the kit as a ZIP. Built on `http.server` — no Flask, no npm.

---

## Customising the structure

Every node supports:

| Key | Required | Description |
|---|---|---|
| `path` | no | Folder name on disk. Defaults to the JSON key. Supports `{brand}`. |
| `title_en` / `title_fa` | no | Human-readable heading. Falls back to the key. |
| `description_en` / `description_fa` | recommended | Body text of the folder's README. |
| `sample_files` | no | Placeholder file names to create. |
| `subdirs` | no | Nested nodes, same shape. |

A top-level `$meta` block (`name_en`, `name_fa`, `default_brand`, `version`)
describes the template itself and is ignored when building the tree.

```json
{
  "$schema": "../structure.schema.json",
  "$meta": {
    "name_en": "My template",
    "name_fa": "قالب من",
    "default_brand": "My"
  },
  "{brand}_Brand_Kit": {
    "title_en": "{brand} Brand Kit",
    "title_fa": "کیت برند {brand}",
    "description_en": "Root folder.",
    "description_fa": "پوشهٔ ریشه.",
    "subdirs": {
      "Logos": {
        "title_en": "Logos",
        "title_fa": "لوگوها",
        "description_en": "All logo files.",
        "description_fa": "همهٔ فایل‌های لوگو.",
        "sample_files": ["logo.svg"]
      }
    }
  }
}
```

Validate it with:

```bash
python scripts/validate_templates.py
```

Unknown keys, non-object nodes, bad `sample_files` types and names that would
collide on case-insensitive file systems are all rejected with a clear message
before anything is written.

---

## Safety notes

- **Idempotent.** Re-running adds missing folders and leaves your edited README
  files untouched. Use `--force` only when you want them reset.
- **No path escapes.** `../`, absolute paths and separators inside a node name
  are sanitised into a single safe component, and every resulting path is
  verified to stay inside the destination.

---

## Development

```bash
pip install -e ".[dev]"
ruff check . && mypy && pytest && python scripts/validate_templates.py
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CHANGELOG.md`](CHANGELOG.md) and the
technical review in [`REVIEW.md`](REVIEW.md).

## Releasing

A step-by-step release guide (GitHub + PyPI) is available in Persian:
[`PUBLISHING.fa.md`](PUBLISHING.fa.md).

## License

[MIT](LICENSE) © borodayeh
