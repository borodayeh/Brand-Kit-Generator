"""Template files and structure validation."""

from __future__ import annotations

import json

import pytest

from brand_kit_generator import cli
from brand_kit_generator.cli import StructureError, validate_structure

TEMPLATES = sorted(cli.available_templates().items())


def test_templates_exist():
    names = {name for name, _ in TEMPLATES}
    assert {"full", "minimal", "startup", "agency"} <= names


@pytest.mark.parametrize("name, path", TEMPLATES, ids=[n for n, _ in TEMPLATES])
def test_template_is_valid(name, path):
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes, meta = cli.split_meta(data)
    assert nodes, f"{name} has no nodes"
    assert meta.get("default_brand"), f"{name} has no default_brand"
    assert meta.get("name_en") and meta.get("name_fa")
    validate_structure(nodes)


@pytest.mark.parametrize("name, path", TEMPLATES, ids=[n for n, _ in TEMPLATES])
def test_template_is_fully_bilingual(name, path):
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes, _ = cli.split_meta(data)
    missing: list[str] = []

    def walk(items, trail=""):
        for key, item in items.items():
            where = f"{trail}/{key}" if trail else key
            for field in ("title_en", "title_fa",
                          "description_en", "description_fa"):
                if not item.get(field):
                    missing.append(f"{where}:{field}")
            if isinstance(item.get("subdirs"), dict):
                walk(item["subdirs"], where)

    walk(nodes)
    assert not missing, f"{name} is missing: {missing}"


def test_full_template_node_count():
    nodes, _ = cli.split_meta(
        json.loads(cli.available_templates()["full"].read_text(encoding="utf-8"))
    )
    count = 0

    def walk(items):
        nonlocal count
        for item in items.values():
            count += 1
            if isinstance(item.get("subdirs"), dict):
                walk(item["subdirs"])

    walk(nodes)
    assert count == 55


def test_schema_file_is_valid_json():
    schema = json.loads(cli.SCHEMA_FILE.read_text(encoding="utf-8"))
    assert schema["$defs"]["node"]["additionalProperties"] is False


def test_rejects_non_object_node():
    with pytest.raises(StructureError, match="must be an object"):
        validate_structure({"A": "oops"})


def test_rejects_unknown_key():
    with pytest.raises(StructureError, match="unknown key"):
        validate_structure({"A": {"typo": 1}})


def test_rejects_bad_sample_files():
    with pytest.raises(StructureError, match="sample_files"):
        validate_structure({"A": {"sample_files": "logo.svg"}})


def test_rejects_case_insensitive_collision():
    with pytest.raises(StructureError, match="collides"):
        validate_structure({"Logos": {}, "LOGOS": {}})


def test_validates_nested_nodes():
    with pytest.raises(StructureError, match="A/B"):
        validate_structure({"A": {"subdirs": {"B": {"nope": 1}}}})


def test_apply_brand_replaces_placeholder():
    structure = {
        "{brand}_Kit": {
            "title_en": "{brand} Kit",
            "description_fa": "کیت {brand}",
            "subdirs": {"Logos": {"title_en": "{brand} Logos"}},
        }
    }
    out = cli.apply_brand(structure, "Acme Corp")
    assert "Acme_Corp_Kit" in out
    node = out["Acme_Corp_Kit"]
    assert node["title_en"] == "Acme Corp Kit"
    assert node["description_fa"] == "کیت Acme Corp"
    assert node["subdirs"]["Logos"]["title_en"] == "Acme Corp Logos"


def test_apply_brand_does_not_mutate_input():
    structure = {"{brand}_Kit": {"title_en": "{brand}"}}
    cli.apply_brand(structure, "Acme")
    assert "{brand}_Kit" in structure
    assert structure["{brand}_Kit"]["title_en"] == "{brand}"
