"""Path sanitisation and traversal protection."""

from __future__ import annotations

import pytest

from brand_kit_generator import cli
from brand_kit_generator.cli import StructureError, safe_join, sanitize_component


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Logos", "Logos"),
        ("  Logos  ", "Logos"),
        ("00_Legal_&_Licensing", "00_Legal_&_Licensing"),
        ("a/b", "a_b"),
        ("a\\b", "a_b"),
        ("../../etc", ".._.._etc"),
        ("/absolute", "_absolute"),
        ("C:\\Windows", "C__Windows"),
        ('bad"name', "bad_name"),
        ("name<>|?*", "name_____"),
        ("trailing...", "trailing"),
        ("trailing   ", "trailing"),
        ("..", "__"),
        (".", "_"),
        ("...", "___"),
        ("CON", "_CON"),
        ("com1.txt", "_com1.txt"),
        ("nul", "_nul"),
        ("normal.txt", "normal.txt"),
    ],
)
def test_sanitize_component(raw, expected):
    assert sanitize_component(raw) == expected


def test_sanitize_strips_control_characters():
    assert sanitize_component("na\x00me\x1f") == "name"


@pytest.mark.parametrize("raw", ["", "   ", "\x00", None, 42])
def test_sanitize_rejects_unusable_names(raw):
    with pytest.raises(StructureError):
        sanitize_component(raw)


def test_safe_join_allows_child(tmp_path):
    assert safe_join(tmp_path, "child") == (tmp_path / "child").resolve()


def test_safe_join_rejects_escape(tmp_path):
    with pytest.raises(StructureError):
        safe_join(tmp_path, "../escape")


def test_slugify_brand():
    assert cli.slugify_brand("Acme Corp") == "Acme_Corp"
    assert cli.slugify_brand("  a/b  ") == "a_b"
    assert cli.slugify_brand("///") == cli.DEFAULT_BRAND
