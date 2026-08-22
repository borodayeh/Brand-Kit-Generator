#!/usr/bin/env python3
"""
Brand Kit Generator / مولد کیت برند
===================================

Creates a comprehensive, bilingual (Persian/English) brand-kit folder
structure from a declarative JSON definition.

یک ساختار پوشه‌ای جامع و دوزبانه (فارسی/انگلیسی) برای کیت برند،
بر اساس یک تعریف JSON اعلانی می‌سازد.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import locale
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

__version__ = "3.0.0"

# --------------------------------------------------------------------------- #
# Constants / ثابت‌ها
# --------------------------------------------------------------------------- #

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
SCHEMA_FILE = PACKAGE_DIR / "structure.schema.json"
DEFAULT_TEMPLATE = "full"

LANGUAGES = ("fa", "en", "both")
DEFAULT_LANG = "both"

BRAND_PLACEHOLDER = "{brand}"
DEFAULT_BRAND = "Ultimate"

# Characters that are illegal in Windows file names (and path separators).
INVALID_CHARS = '<>:"/\\|?*'

# Reserved device names on Windows.
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

# Conservative limit to stay clear of the Windows MAX_PATH (260) restriction.
MAX_PATH_WARN = 240

# Binary asset patterns tracked with Git LFS when --git-init is used.
LFS_PATTERNS = (
    "*.ai", "*.psd", "*.indd", "*.eps", "*.sketch", "*.fig", "*.xd",
    "*.pdf", "*.zip", "*.mp4", "*.mov", "*.aep", "*.wav", "*.mp3",
    "*.otf", "*.ttf", "*.woff", "*.woff2",
)

# Exit codes / کدهای خروج
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_INVALID_INPUT = 2
EXIT_ABORTED = 130

# --------------------------------------------------------------------------- #
# Bilingual messages / پیام‌های دوزبانه
# --------------------------------------------------------------------------- #

MESSAGES: dict[str, dict[str, str]] = {
    "enter_path": {
        "en": "Please enter the full path to create the brand kit: ",
        "fa": "لطفاً مسیر کامل برای ساخت کیت برند را وارد کنید: ",
    },
    "no_path": {
        "en": "No path entered. Operation canceled.",
        "fa": "مسیری وارد نشد. عملیات لغو شد.",
    },
    "aborted": {
        "en": "Operation canceled by the user.",
        "fa": "عملیات توسط کاربر لغو شد.",
    },
    "file_not_found": {
        "en": "Error: The structure file '{path}' was not found.",
        "fa": "خطا: فایل ساختار «{path}» پیدا نشد.",
    },
    "unknown_template": {
        "en": "Error: Unknown template '{name}'. Available: {available}",
        "fa": "خطا: قالب «{name}» شناخته نشد. قالب‌های موجود: {available}",
    },
    "invalid_json": {
        "en": "Error: '{path}' is not a valid JSON file ({detail}).",
        "fa": "خطا: فایل «{path}» یک JSON معتبر نیست ({detail}).",
    },
    "invalid_structure": {
        "en": "Error: Invalid structure definition: {detail}",
        "fa": "خطا: تعریف ساختار نامعتبر است: {detail}",
    },
    "empty_structure": {
        "en": "Error: The structure file is empty.",
        "fa": "خطا: فایل ساختار خالی است.",
    },
    "templates_title": {
        "en": "Available templates:",
        "fa": "قالب‌های موجود:",
    },
    "path_created": {
        "en": "The path '{path}' did not exist and has been created.",
        "fa": "مسیر «{path}» وجود نداشت و ساخته شد.",
    },
    "cannot_create_path": {
        "en": "Error: Unable to create the directory '{path}': {detail}",
        "fa": "خطا: امکان ساخت پوشهٔ «{path}» وجود ندارد: {detail}",
    },
    "not_a_directory": {
        "en": "Error: '{path}' exists but is not a directory.",
        "fa": "خطا: «{path}» وجود دارد اما یک پوشه نیست.",
    },
    "no_write_permission": {
        "en": "Error: No write permission for the path '{path}'.",
        "fa": "خطا: اجازهٔ نوشتن در مسیر «{path}» وجود ندارد.",
    },
    "working": {
        "en": "Creating the brand kit folder structure...",
        "fa": "در حال ساخت ساختار پوشه‌ای کیت برند...",
    },
    "dry_run_notice": {
        "en": "DRY RUN - no files or folders will be written.",
        "fa": "اجرای آزمایشی - هیچ فایل یا پوشه‌ای نوشته نخواهد شد.",
    },
    "dir_created": {
        "en": "Directory created: {path}",
        "fa": "پوشه ساخته شد: {path}",
    },
    "dir_exists": {
        "en": "Directory already exists: {path}",
        "fa": "پوشه از قبل وجود دارد: {path}",
    },
    "file_written": {
        "en": "File written: {path}",
        "fa": "فایل نوشته شد: {path}",
    },
    "file_skipped": {
        "en": "Skipped (already exists): {path}",
        "fa": "رد شد (از قبل وجود دارد): {path}",
    },
    "long_path_warning": {
        "en": "Warning: path exceeds {limit} characters and may fail on Windows: {path}",
        "fa": "هشدار: طول مسیر از {limit} کاراکتر بیشتر است و ممکن است در ویندوز خطا بدهد: {path}",
    },
    "node_error": {
        "en": "Error while processing '{name}': {detail}",
        "fa": "خطا هنگام پردازش «{name}»: {detail}",
    },
    "zip_created": {
        "en": "Archive created: {path}",
        "fa": "فایل فشرده ساخته شد: {path}",
    },
    "zip_failed": {
        "en": "Error: Could not create the archive: {detail}",
        "fa": "خطا: ساخت فایل فشرده ممکن نشد: {detail}",
    },
    "git_initialised": {
        "en": "Git repository initialised in: {path}",
        "fa": "مخزن گیت در این مسیر مقداردهی شد: {path}",
    },
    "git_missing": {
        "en": "Warning: 'git' was not found on PATH; skipping --git-init.",
        "fa": "هشدار: دستور «git» پیدا نشد؛ از --git-init صرف‌نظر شد.",
    },
    "git_failed": {
        "en": "Warning: git init failed: {detail}",
        "fa": "هشدار: اجرای git init ناموفق بود: {detail}",
    },
    "summary_title": {
        "en": "Summary",
        "fa": "خلاصهٔ عملیات",
    },
    "summary_dirs": {
        "en": "Directories created : {n}",
        "fa": "پوشه‌های ساخته‌شده : {n}",
    },
    "summary_existing": {
        "en": "Directories existing: {n}",
        "fa": "پوشه‌های موجود      : {n}",
    },
    "summary_files": {
        "en": "Files written       : {n}",
        "fa": "فایل‌های نوشته‌شده  : {n}",
    },
    "summary_skipped": {
        "en": "Files skipped       : {n}",
        "fa": "فایل‌های ردشده     : {n}",
    },
    "summary_errors": {
        "en": "Errors              : {n}",
        "fa": "خطاها              : {n}",
    },
    "skip_hint": {
        "en": "Existing files were preserved. Use --force to overwrite them.",
        "fa": "فایل‌های موجود دست‌نخورده باقی ماندند. برای بازنویسی از --force استفاده کنید.",
    },
    "success": {
        "en": "Operation completed successfully.",
        "fa": "عملیات با موفقیت انجام شد.",
    },
    "success_dry": {
        "en": "Dry run completed. Nothing was written.",
        "fa": "اجرای آزمایشی کامل شد. چیزی نوشته نشد.",
    },
    "finished_with_errors": {
        "en": "Finished with {n} error(s). The structure may be incomplete.",
        "fa": "عملیات با {n} خطا به پایان رسید. ساختار ممکن است ناقص باشد.",
    },
    "output_location": {
        "en": "Brand kit location:",
        "fa": "محل کیت برند:",
    },
    "readme_generated_by": {
        "en": "Generated by Brand Kit Generator v{version}",
        "fa": "تولیدشده توسط مولد کیت برند نسخهٔ {version}",
    },
    "sample_file_note": {
        "en": "Placeholder file for '{name}'. Replace it with the real asset.",
        "fa": "فایل جانگهدار برای «{name}». آن را با فایل واقعی جایگزین کنید.",
    },
    "manifest_title": {
        "en": "Brand Kit Manifest",
        "fa": "فهرست کیت برند",
    },
    "manifest_brand": {"en": "Brand", "fa": "برند"},
    "manifest_template": {"en": "Template", "fa": "قالب"},
    "manifest_created": {"en": "Created", "fa": "تاریخ ساخت"},
    "manifest_generator": {"en": "Generator", "fa": "تولیدکننده"},
    "manifest_tree": {"en": "Folder tree", "fa": "درخت پوشه‌ها"},
}


def t(key: str, lang: str, **kwargs: Any) -> str:
    """Translate a message key. `lang` may be 'fa', 'en' or 'both'."""
    entry = MESSAGES[key]
    if lang == "both":
        return f"{entry['en'].format(**kwargs)}\n{entry['fa'].format(**kwargs)}"
    return entry[lang].format(**kwargs)


def t_inline(key: str, lang: str, **kwargs: Any) -> str:
    """Like `t()`, but keeps bilingual output on a single line."""
    entry = MESSAGES[key]
    if lang == "both":
        return f"{entry['en'].format(**kwargs)} · {entry['fa'].format(**kwargs)}"
    return entry[lang].format(**kwargs)


def detect_language() -> str:
    """Guess the UI language from the environment; falls back to bilingual."""
    for var in ("BRANDKIT_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if not value:
            continue
        lowered = value.lower()
        if lowered.startswith(("fa", "per")):
            return "fa"
        if lowered.startswith("en"):
            return "en"
    try:
        code = (locale.getlocale()[0] or "").lower()
    except (ValueError, TypeError):  # pragma: no cover - platform dependent
        code = ""
    if code.startswith("fa"):
        return "fa"
    return DEFAULT_LANG


# --------------------------------------------------------------------------- #
# Console helpers / کمک‌کننده‌های کنسول
# --------------------------------------------------------------------------- #

def configure_stdio() -> None:
    """Make sure Persian text and symbols survive legacy Windows code pages."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        # pragma: no cover - platform dependent
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8", errors="replace")


class Reporter:
    """Tiny leveled printer: quiet (-q), normal, verbose (-v)."""

    def __init__(self, lang: str, verbose: bool = False, quiet: bool = False) -> None:
        self.lang = lang
        self.verbose = verbose
        self.quiet = quiet

    def _write(self, text: str, stream: Any = None) -> None:
        print(text, file=stream or sys.stdout)

    def info(self, key: str, **kwargs: Any) -> None:
        if not self.quiet:
            self._write(t(key, self.lang, **kwargs))

    def detail(self, key: str, **kwargs: Any) -> None:
        if self.verbose and not self.quiet:
            self._write(t(key, self.lang, **kwargs))

    def warn(self, key: str, **kwargs: Any) -> None:
        if not self.quiet:
            self._write(t(key, self.lang, **kwargs), stream=sys.stderr)

    def error(self, key: str, **kwargs: Any) -> None:
        self._write(t(key, self.lang, **kwargs), stream=sys.stderr)

    def raw(self, text: str = "") -> None:
        if not self.quiet:
            self._write(text)


# --------------------------------------------------------------------------- #
# Path sanitisation / پاک‌سازی مسیر
# --------------------------------------------------------------------------- #

class StructureError(Exception):
    """Raised when the structure definition is invalid or unsafe."""


def sanitize_component(raw_name: str) -> str:
    """
    Turn an arbitrary string into a single, safe path component.

    Path separators, parent references, control characters, Windows-illegal
    characters and reserved device names are all neutralised, so a malformed
    or malicious structure file can never escape the destination directory.
    """
    if not isinstance(raw_name, str):
        raise StructureError(f"folder name must be a string, got {type(raw_name).__name__}")

    name = raw_name.strip()
    if not name:
        raise StructureError("empty folder name")

    # Drop control characters.
    name = "".join(ch for ch in name if ord(ch) >= 32 and ch != "\x7f")

    # Replace every illegal character, including separators.
    for ch in INVALID_CHARS:
        name = name.replace(ch, "_")

    # Neutralise parent/current directory references.
    if set(name) == {"."}:
        name = "_" * len(name)

    # Windows forbids trailing dots and spaces.
    name = name.rstrip(" .")

    if not name:
        raise StructureError(f"folder name '{raw_name}' reduces to an empty string")

    # Reserved device names (with or without an extension).
    stem = name.split(".", 1)[0].upper()
    if stem in WINDOWS_RESERVED:
        name = f"_{name}"

    return name


def safe_join(base: Path, component: str) -> Path:
    """Join a sanitised component to `base` and assert it stays inside it."""
    candidate = (base / component).resolve()
    base_resolved = base.resolve()
    if candidate != base_resolved and base_resolved not in candidate.parents:
        raise StructureError(f"path escapes the destination directory: {component}")
    return candidate


def slugify_brand(brand: str) -> str:
    """Make a brand name safe for use inside a folder name."""
    slug = re.sub(r"\s+", "_", brand.strip())
    slug = "".join("_" if ch in INVALID_CHARS else ch for ch in slug)
    slug = re.sub(r"_{2,}", "_", slug).strip("_ .")
    return slug or DEFAULT_BRAND


# --------------------------------------------------------------------------- #
# Templates / قالب‌ها
# --------------------------------------------------------------------------- #

def available_templates() -> dict[str, Path]:
    """Map template name -> file path."""
    if not TEMPLATES_DIR.is_dir():
        return {}
    return {p.stem: p for p in sorted(TEMPLATES_DIR.glob("*.json"))}


def template_meta(path: Path) -> dict[str, Any]:
    """Read the `$meta` block of a template without full validation."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    meta = data.get("$meta") if isinstance(data, dict) else None
    return meta if isinstance(meta, dict) else {}


def print_templates(lang: str) -> int:
    """Implementation of --list-templates."""
    templates = available_templates()
    print(t("templates_title", lang))
    for name, path in templates.items():
        meta = template_meta(path)
        if lang == "fa":
            label = meta.get("name_fa") or meta.get("name_en") or ""
        elif lang == "en":
            label = meta.get("name_en") or ""
        else:
            parts = [meta.get("name_en"), meta.get("name_fa")]
            label = " · ".join(p for p in parts if p)
        marker = " (default)" if name == DEFAULT_TEMPLATE else ""
        print(f"  {name}{marker}{' — ' + label if label else ''}")
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Structure loading & validation / بارگذاری و اعتبارسنجی ساختار
# --------------------------------------------------------------------------- #

ALLOWED_KEYS = {
    "path", "title_fa", "title_en",
    "description_fa", "description_en",
    "subdirs", "sample_files",
}

META_KEYS = ("$schema", "$meta")


def split_meta(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Separate `$`-prefixed metadata keys from the actual nodes."""
    raw_meta = data.get("$meta")
    meta: dict[str, Any] = dict(raw_meta) if isinstance(raw_meta, dict) else {}
    nodes = {k: v for k, v in data.items() if not k.startswith("$")}
    return nodes, meta


def load_structure(file_path: Path, reporter: Reporter
                   ) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Load and validate a structure definition. Returns (nodes, meta) or None."""
    try:
        raw = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        reporter.error("file_not_found", path=file_path)
        return None
    except OSError as exc:
        reporter.error("file_not_found", path=f"{file_path} ({exc})")
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        reporter.error("invalid_json", path=file_path, detail=exc)
        return None

    if not isinstance(data, dict):
        reporter.error("empty_structure")
        return None

    nodes, meta = split_meta(data)
    if not nodes:
        reporter.error("empty_structure")
        return None

    try:
        validate_structure(nodes)
    except StructureError as exc:
        reporter.error("invalid_structure", detail=exc)
        return None

    return nodes, meta


def validate_structure(structure: dict[str, Any], trail: str = "") -> None:
    """Recursively check the shape of the structure definition."""
    if not isinstance(structure, dict):
        raise StructureError(f"'{trail or 'root'}' must be an object")

    seen: dict[str, str] = {}
    for name, item in structure.items():
        where = f"{trail}/{name}" if trail else name

        if not isinstance(item, dict):
            raise StructureError(f"'{where}' must be an object")

        unknown = set(item) - ALLOWED_KEYS
        if unknown:
            raise StructureError(f"'{where}' has unknown key(s): {', '.join(sorted(unknown))}")

        folder = sanitize_component(str(item.get("path") or name))

        # Case-insensitive collision (macOS/Windows file systems).
        lowered = folder.lower()
        if lowered in seen:
            raise StructureError(
                f"'{where}' collides with '{seen[lowered]}' on case-insensitive file systems"
            )
        seen[lowered] = where

        samples = item.get("sample_files", [])
        if not isinstance(samples, list) or not all(isinstance(s, str) for s in samples):
            raise StructureError(f"'{where}'.sample_files must be a list of strings")

        subdirs = item.get("subdirs")
        if subdirs is not None:
            validate_structure(subdirs, where)


def apply_brand(structure: dict[str, Any], brand: str) -> dict[str, Any]:
    """Replace `{brand}` in names, titles and descriptions."""
    slug = slugify_brand(brand)

    def walk(nodes: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for name, item in nodes.items():
            new_item = dict(item)
            for key in ("path", "title_en", "title_fa",
                        "description_en", "description_fa"):
                value = new_item.get(key)
                if isinstance(value, str) and BRAND_PLACEHOLDER in value:
                    repl = slug if key == "path" else brand
                    new_item[key] = value.replace(BRAND_PLACEHOLDER, repl)
            if "path" not in new_item and BRAND_PLACEHOLDER in name:
                new_item["path"] = name.replace(BRAND_PLACEHOLDER, slug)
            if isinstance(new_item.get("subdirs"), dict):
                new_item["subdirs"] = walk(new_item["subdirs"])
            out[name.replace(BRAND_PLACEHOLDER, slug)] = new_item
        return out

    return walk(structure)


def root_names(structure: dict[str, Any]) -> list[str]:
    """Sanitised names of the top-level folders."""
    return [sanitize_component(str(item.get("path") or name))
            for name, item in structure.items()]


# --------------------------------------------------------------------------- #
# README rendering / ساخت محتوای README
# --------------------------------------------------------------------------- #

def humanize(name: str) -> str:
    """'06_Favicons_&_App_Icons' -> 'Favicons & App Icons'"""
    cleaned = name.replace("_", " ").strip()
    parts = cleaned.split(" ", 1)
    if len(parts) == 2 and parts[0].isdigit():
        cleaned = parts[1]
    return cleaned.strip()


def node_title(item: dict[str, Any], name: str, lang: str) -> str:
    """Best available display title for a node in the requested language."""
    fallback = humanize(name)
    if lang == "fa":
        return str(item.get("title_fa") or item.get("title_en") or fallback)
    return str(item.get("title_en") or fallback)


def render_readme(name: str, item: dict[str, Any], lang: str) -> str:
    """
    Build a Markdown README for one folder.

    Persian content is wrapped in `<div dir="rtl">` so it renders correctly
    (right-to-left) on GitHub, GitLab and most Markdown viewers.
    """
    title_en = str(item.get("title_en") or humanize(name))
    title_fa = str(item.get("title_fa") or title_en)
    desc_en = str(item.get("description_en") or "No description available.")
    desc_fa = str(item.get("description_fa") or "توضیحی موجود نیست.")

    lines: list[str]
    if lang == "en":
        lines = [f"# {title_en}", "", desc_en, ""]
    elif lang == "fa":
        lines = [
            f"# {title_fa}", "",
            '<div dir="rtl">', "",
            desc_fa, "",
            "</div>", "",
        ]
    else:
        lines = [
            f"# {title_en} / {title_fa}", "",
            "## English", "",
            f"**{title_en}**", "",
            desc_en, "",
            "---", "",
            '<div dir="rtl">', "",
            "## فارسی", "",
            f"**{title_fa}**", "",
            desc_fa, "",
            "</div>", "",
        ]

    footer = t_inline("readme_generated_by", lang, version=__version__)
    lines += ["---", "", f"<sub>{footer}</sub>", ""]
    return "\n".join(lines)


def render_sample(item: dict[str, Any], name: str, file_name: str, lang: str) -> str:
    """Content for a placeholder asset file."""
    note = t_inline("sample_file_note", lang, name=node_title(item, name, lang))
    return f"{file_name}\n\n{note}\n"


def render_manifest(structure: dict[str, Any], lang: str, brand: str,
                    template: str) -> str:
    """A single overview file listing the whole generated tree."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    tree: list[str] = []

    def walk(nodes: dict[str, Any], depth: int) -> None:
        for name, item in nodes.items():
            folder = sanitize_component(str(item.get("path") or name))
            title = node_title(item, name, "en" if lang == "en" else "fa")
            tree.append(f"{'  ' * depth}- `{folder}` — {title}")
            if isinstance(item.get("subdirs"), dict):
                walk(item["subdirs"], depth + 1)

    walk(structure, 0)

    def row(key: str, value: str) -> str:
        return f"| {t_inline(key, lang)} | {value} |"

    lines = [
        f"# {t_inline('manifest_title', lang)}",
        "",
        "| | |",
        "|---|---|",
        row("manifest_brand", brand),
        row("manifest_template", template),
        row("manifest_created", stamp),
        row("manifest_generator", f"Brand Kit Generator v{__version__}"),
        "",
        f"## {t_inline('manifest_tree', lang)}",
        "",
    ]
    lines += tree
    lines += ["", "---", "",
              f"<sub>{t_inline('readme_generated_by', lang, version=__version__)}</sub>", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Generation / تولید ساختار
# --------------------------------------------------------------------------- #

@dataclass
class Stats:
    dirs_created: int = 0
    dirs_existing: int = 0
    files_written: int = 0
    files_skipped: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class Options:
    lang: str = DEFAULT_LANG
    force: bool = False
    dry_run: bool = False
    samples: bool = True
    manifest: bool = True
    brand: str = DEFAULT_BRAND
    template: str = DEFAULT_TEMPLATE


def _write_file(path: Path, content: str, opts: Options,
                stats: Stats, reporter: Reporter) -> None:
    """Write a file unless it exists (or --force), honouring --dry-run."""
    if path.exists() and not opts.force:
        stats.files_skipped += 1
        reporter.detail("file_skipped", path=path)
        return

    if not opts.dry_run:
        path.write_text(content, encoding="utf-8")
    stats.files_written += 1
    reporter.detail("file_written", path=path)


def create_structure(base_path: Path, structure: dict[str, Any], opts: Options,
                     stats: Stats, reporter: Reporter) -> None:
    """
    Recursively create folders, README files and placeholder assets.

    Errors are collected instead of aborting, so a single unwritable folder
    does not silently truncate the rest of the tree.
    """
    for name, item in structure.items():
        try:
            folder = sanitize_component(str(item.get("path") or name))
            full_path = safe_join(base_path, folder)

            if len(str(full_path)) > MAX_PATH_WARN:
                reporter.warn("long_path_warning", limit=MAX_PATH_WARN, path=full_path)

            if full_path.exists():
                if not full_path.is_dir():
                    raise StructureError(f"'{full_path}' exists and is not a directory")
                stats.dirs_existing += 1
                reporter.detail("dir_exists", path=full_path)
            else:
                if not opts.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                stats.dirs_created += 1
                reporter.detail("dir_created", path=full_path)

            _write_file(
                full_path / "README.md",
                render_readme(name, item, opts.lang),
                opts, stats, reporter,
            )

            if opts.samples:
                for raw_file in item.get("sample_files", []):
                    file_name = sanitize_component(raw_file)
                    _write_file(
                        safe_join(full_path, file_name),
                        render_sample(item, name, file_name, opts.lang),
                        opts, stats, reporter,
                    )

            subdirs = item.get("subdirs")
            if subdirs:
                create_structure(full_path, subdirs, opts, stats, reporter)

        except (OSError, StructureError) as exc:
            stats.errors.append(f"{name}: {exc}")
            reporter.error("node_error", name=name, detail=exc)


def generate(base_path: Path, structure: dict[str, Any], opts: Options,
             reporter: Reporter) -> Stats:
    """Create the whole kit plus the optional manifest."""
    stats = Stats()
    create_structure(base_path, structure, opts, stats, reporter)

    if opts.manifest:
        try:
            _write_file(
                base_path / "MANIFEST.md",
                render_manifest(structure, opts.lang, opts.brand, opts.template),
                opts, stats, reporter,
            )
        except OSError as exc:
            stats.errors.append(f"MANIFEST.md: {exc}")
            reporter.error("node_error", name="MANIFEST.md", detail=exc)

    return stats


# --------------------------------------------------------------------------- #
# Extras: zip + git / امکانات جانبی
# --------------------------------------------------------------------------- #

def make_archive(base_path: Path, roots: Iterable[str], zip_path: Path) -> Path:
    """Zip the generated root folders (plus MANIFEST.md if present)."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        manifest = base_path / "MANIFEST.md"
        if manifest.is_file():
            archive.write(manifest, "MANIFEST.md")
        for root in roots:
            root_path = base_path / root
            if not root_path.is_dir():
                continue
            for item in sorted(root_path.rglob("*")):
                archive.write(item, str(item.relative_to(base_path)))
    return zip_path


GIT_IGNORE = """\
# OS noise
.DS_Store
Thumbs.db

# Working files
*.tmp
*~
"""


def init_git_repo(base_path: Path, reporter: Reporter) -> bool:
    """`git init` the destination and add LFS tracking for binary assets."""
    if shutil.which("git") is None:
        reporter.warn("git_missing")
        return False

    (base_path / ".gitignore").write_text(GIT_IGNORE, encoding="utf-8")
    attributes = "\n".join(
        f"{pattern} filter=lfs diff=lfs merge=lfs -text" for pattern in LFS_PATTERNS
    )
    (base_path / ".gitattributes").write_text(attributes + "\n", encoding="utf-8")

    try:
        subprocess.run(
            ["git", "init", "--quiet"], cwd=str(base_path),
            check=True, capture_output=True,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        reporter.warn("git_failed", detail=exc)
        return False

    reporter.info("git_initialised", path=base_path)
    return True


# --------------------------------------------------------------------------- #
# Destination handling / آماده‌سازی مقصد
# --------------------------------------------------------------------------- #

def resolve_destination(raw: str) -> Path:
    """Expand `~`, environment variables and relative segments."""
    return Path(os.path.expandvars(raw.strip())).expanduser().resolve()


def prepare_destination(base_path: Path, opts: Options, reporter: Reporter) -> bool:
    """Create/validate the destination directory. Returns False on failure."""
    if base_path.exists():
        if not base_path.is_dir():
            reporter.error("not_a_directory", path=base_path)
            return False
    elif opts.dry_run:
        reporter.info("path_created", path=base_path)
        return True
    else:
        try:
            base_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            reporter.error("cannot_create_path", path=base_path, detail=exc)
            return False
        reporter.info("path_created", path=base_path)

    if not os.access(base_path, os.W_OK):
        reporter.error("no_write_permission", path=base_path)
        return False
    return True


# --------------------------------------------------------------------------- #
# Reporting / گزارش پایانی
# --------------------------------------------------------------------------- #

def print_summary(stats: Stats, base_path: Path, roots: Iterable[str],
                  opts: Options, reporter: Reporter) -> None:
    reporter.raw()
    reporter.info("summary_title")
    reporter.raw("-" * 46)
    reporter.info("summary_dirs", n=stats.dirs_created)
    reporter.info("summary_existing", n=stats.dirs_existing)
    reporter.info("summary_files", n=stats.files_written)
    reporter.info("summary_skipped", n=stats.files_skipped)
    reporter.info("summary_errors", n=len(stats.errors))
    reporter.raw("-" * 46)

    if stats.files_skipped and not opts.force:
        reporter.info("skip_hint")

    reporter.raw()
    if stats.errors:
        reporter.error("finished_with_errors", n=len(stats.errors))
    elif opts.dry_run:
        reporter.info("success_dry")
    else:
        reporter.info("success")

    reporter.raw()
    reporter.info("output_location")
    for root in roots:
        reporter.raw(f"  {base_path / root}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brandkit",
        description=(
            "Create a bilingual (fa/en) brand kit folder structure.  |  "
            "ساخت ساختار پوشه‌ای دوزبانه (فارسی/انگلیسی) برای کیت برند."
        ),
        epilog=(
            "Examples / نمونه‌ها:\n"
            "  brandkit ./MyBrand\n"
            "  brandkit ./MyBrand --brand Acme --template startup --lang fa\n"
            "  brandkit ./MyBrand --zip Acme_brand_kit.zip --git-init\n"
            "  brandkit --list-templates\n"
            "  brandkit --web\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path", nargs="?",
        help="Destination directory (prompted if omitted) / پوشهٔ مقصد",
    )
    parser.add_argument(
        "-t", "--template", default=DEFAULT_TEMPLATE,
        help="Built-in template name / نام قالب آماده (default: %(default)s)",
    )
    parser.add_argument(
        "-s", "--structure", type=Path, default=None,
        help="Custom structure JSON file (overrides --template) / فایل ساختار سفارشی",
    )
    parser.add_argument(
        "-b", "--brand", default=None,
        help="Brand name substituted for {brand} / نام برند جایگزین {brand}",
    )
    parser.add_argument(
        "-l", "--lang", choices=LANGUAGES, default=None,
        help="Output/UI language / زبان خروجی و رابط (default: auto)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true",
        help="Overwrite existing files / بازنویسی فایل‌های موجود",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Show what would happen without writing / اجرای آزمایشی",
    )
    parser.add_argument(
        "--no-samples", action="store_true",
        help="Do not create placeholder asset files / بدون فایل‌های نمونه",
    )
    parser.add_argument(
        "--no-manifest", action="store_true",
        help="Do not create MANIFEST.md / بدون ساخت فایل فهرست",
    )
    parser.add_argument(
        "-z", "--zip", metavar="FILE", nargs="?", const="", default=None,
        help="Also create a ZIP archive / ساخت فایل فشرده",
    )
    parser.add_argument(
        "--git-init", action="store_true",
        help="Initialise a git repo with LFS rules / ساخت مخزن گیت با قواعد LFS",
    )
    parser.add_argument(
        "--list-templates", action="store_true",
        help="List the built-in templates and exit / نمایش قالب‌های آماده",
    )
    parser.add_argument(
        "--web", action="store_true",
        help="Start the local web interface / اجرای رابط وب محلی",
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Web interface host / میزبان رابط وب (default: %(default)s)",
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Web interface port / درگاه رابط وب (default: %(default)s)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Show every created path / نمایش جزئیات",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Print errors only / فقط نمایش خطاها",
    )
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"Brand Kit Generator {__version__}",
    )
    return parser


def resolve_structure_file(args: argparse.Namespace, lang: str,
                           reporter: Reporter) -> Path | None:
    """Pick the structure file from --structure or --template."""
    if args.structure is not None:
        return args.structure

    templates = available_templates()
    if args.template not in templates:
        reporter.error("unknown_template", name=args.template,
                       available=", ".join(templates) or "-")
        return None
    return templates[args.template]


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    args = build_parser().parse_args(argv)

    lang = args.lang or detect_language()
    reporter = Reporter(lang, verbose=args.verbose, quiet=args.quiet)

    if args.list_templates:
        return print_templates(lang)

    if args.web:
        from . import webapp
        return webapp.serve(host=args.host, port=args.port, lang=lang)

    structure_file = resolve_structure_file(args, lang, reporter)
    if structure_file is None:
        return EXIT_INVALID_INPUT

    loaded = load_structure(structure_file, reporter)
    if loaded is None:
        return EXIT_INVALID_INPUT
    structure, meta = loaded

    brand = args.brand or str(meta.get("default_brand") or DEFAULT_BRAND)
    structure = apply_brand(structure, brand)

    raw_path = args.path
    if raw_path is None:
        try:
            raw_path = input(t("enter_path", lang))
        except (EOFError, KeyboardInterrupt):
            reporter.raw()
            reporter.error("aborted")
            return EXIT_ABORTED

    if not raw_path or not raw_path.strip():
        reporter.error("no_path")
        return EXIT_INVALID_INPUT

    base_path = resolve_destination(raw_path)

    opts = Options(
        lang=lang,
        force=args.force,
        dry_run=args.dry_run,
        samples=not args.no_samples,
        manifest=not args.no_manifest,
        brand=brand,
        template="custom" if args.structure else args.template,
    )

    if not prepare_destination(base_path, opts, reporter):
        return EXIT_ERROR

    reporter.raw()
    if opts.dry_run:
        reporter.info("dry_run_notice")
    reporter.info("working")
    reporter.raw()

    try:
        stats = generate(base_path, structure, opts, reporter)
    except KeyboardInterrupt:
        reporter.raw()
        reporter.error("aborted")
        return EXIT_ABORTED

    roots = root_names(structure)

    if args.git_init and not opts.dry_run:
        init_git_repo(base_path, reporter)

    if args.zip is not None and not opts.dry_run:
        zip_name = args.zip or f"{slugify_brand(brand)}_brand_kit.zip"
        try:
            created = make_archive(base_path, roots, Path(zip_name).expanduser())
            reporter.info("zip_created", path=created.resolve())
        except OSError as exc:
            reporter.error("zip_failed", detail=exc)
            stats.errors.append(f"zip: {exc}")

    print_summary(stats, base_path, roots, opts, reporter)
    return EXIT_ERROR if stats.errors else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
