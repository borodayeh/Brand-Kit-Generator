"""Rendering of generated Markdown."""

from __future__ import annotations

from brand_kit_generator.cli import humanize, node_title, render_manifest, render_readme

NODE = {
    "title_en": "Primary Logo",
    "title_fa": "لوگوی اصلی",
    "description_en": "The main logo.",
    "description_fa": "لوگوی اصلی برند.",
}


def test_humanize_strips_prefix_and_underscores():
    assert humanize("06_Favicons_&_App_Icons") == "Favicons & App Icons"
    assert humanize("Source_Files") == "Source Files"


def test_readme_both_is_bilingual_and_rtl():
    out = render_readme("01_Primary_Logo", NODE, "both")
    assert out.startswith("# Primary Logo / لوگوی اصلی")
    assert '<div dir="rtl">' in out
    assert "The main logo." in out
    assert "لوگوی اصلی برند." in out


def test_readme_fa_is_rtl_and_has_no_english_body():
    out = render_readme("01_Primary_Logo", NODE, "fa")
    assert out.startswith("# لوگوی اصلی")
    assert '<div dir="rtl">' in out
    assert "The main logo." not in out


def test_readme_en_has_no_rtl_wrapper():
    out = render_readme("01_Primary_Logo", NODE, "en")
    assert "rtl" not in out
    assert "لوگوی اصلی برند." not in out


def test_readme_falls_back_to_humanized_key():
    out = render_readme("01_Primary_Logo", {}, "en")
    assert out.startswith("# Primary Logo")
    assert "No description available." in out


def test_node_title_language_preference():
    assert node_title(NODE, "x", "fa") == "لوگوی اصلی"
    assert node_title(NODE, "x", "en") == "Primary Logo"
    assert node_title({}, "01_Logos", "en") == "Logos"


def test_manifest_lists_the_whole_tree():
    structure = {"Kit": {"title_en": "Kit", "subdirs": {"Logos": {"title_en": "Logos"}}}}
    out = render_manifest(structure, "en", "Acme", "minimal")
    assert "| Brand | Acme |" in out
    assert "`Kit`" in out
    assert "  - `Logos`" in out
