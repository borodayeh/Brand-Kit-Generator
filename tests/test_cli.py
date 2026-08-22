"""End-to-end CLI behaviour, including the historical bug fixes."""

from __future__ import annotations

import json
import zipfile

import pytest

from brand_kit_generator import cli


def test_generates_full_tree(run, dest):
    code, _, _ = run(str(dest), "-q")
    assert code == cli.EXIT_OK
    assert len(list(dest.rglob("*"))) == 55 + 62 + 1  # dirs + files + MANIFEST


def test_runs_from_any_working_directory(run, dest, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, _, _ = run(str(dest), "--template", "minimal", "-q")
    assert code == cli.EXIT_OK
    assert (dest / "My_Brand_Kit" / "README.md").is_file()


# --------------------------------------------------------------------------- #
# Bug #2: existing files must never be clobbered
# --------------------------------------------------------------------------- #

def test_does_not_overwrite_existing_files(run, dest):
    run(str(dest), "--template", "minimal", "-q")
    readme = dest / "My_Brand_Kit" / "README.md"
    readme.write_text("MY NOTES", encoding="utf-8")

    code, _, _ = run(str(dest), "--template", "minimal", "-q")
    assert code == cli.EXIT_OK
    assert readme.read_text(encoding="utf-8") == "MY NOTES"


def test_force_overwrites(run, dest):
    run(str(dest), "--template", "minimal", "-q")
    readme = dest / "My_Brand_Kit" / "README.md"
    readme.write_text("MY NOTES", encoding="utf-8")

    run(str(dest), "--template", "minimal", "-q", "--force")
    assert readme.read_text(encoding="utf-8").startswith("#")


def test_rerun_is_idempotent(run, dest):
    run(str(dest), "--template", "minimal", "-q")
    before = sorted(p.name for p in dest.rglob("*"))
    run(str(dest), "--template", "minimal", "-q")
    assert sorted(p.name for p in dest.rglob("*")) == before


# --------------------------------------------------------------------------- #
# Bug #3: traversal
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("evil", ["../../escape", "/tmp/escape", "..\\..\\escape"])
def test_structure_cannot_escape_destination(run, dest, tmp_path, evil):
    custom = tmp_path / "evil.json"
    custom.write_text(json.dumps({"A": {"path": evil}}), encoding="utf-8")

    run(str(dest), "-s", str(custom), "-q")
    for created in dest.rglob("*"):
        assert dest.resolve() in created.resolve().parents


# --------------------------------------------------------------------------- #
# Bug #4/#5/#6: paths, exit codes, non-interactive input
# --------------------------------------------------------------------------- #

def test_expands_tilde(run, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    run("~/kit", "--template", "minimal", "-q")
    assert (tmp_path / "kit" / "My_Brand_Kit").is_dir()


def test_expands_environment_variables(run, tmp_path, monkeypatch):
    monkeypatch.setenv("BK_TEST_DIR", str(tmp_path / "envdir"))
    run("$BK_TEST_DIR", "--template", "minimal", "-q")
    assert (tmp_path / "envdir" / "My_Brand_Kit").is_dir()


def test_missing_structure_file_exits_2(run, dest, tmp_path):
    code, _, err = run(str(dest), "-s", str(tmp_path / "nope.json"))
    assert code == cli.EXIT_INVALID_INPUT
    assert "not found" in err.lower() or "پیدا نشد" in err


def test_unknown_template_exits_2(run, dest):
    code, _, err = run(str(dest), "--template", "nope")
    assert code == cli.EXIT_INVALID_INPUT
    assert "nope" in err


def test_invalid_json_exits_2(run, dest, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    code, _, _ = run(str(dest), "-s", str(bad))
    assert code == cli.EXIT_INVALID_INPUT


def test_empty_path_exits_2(run):
    code, _, _ = run("")
    assert code == cli.EXIT_INVALID_INPUT


def test_closed_stdin_exits_130(run, monkeypatch):
    def raise_eof(*_args):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    code, _, _ = run()
    assert code == cli.EXIT_ABORTED


def test_prompts_when_path_is_omitted(run, dest):
    code, _, _ = run("--template", "minimal", "-q", stdin=str(dest))
    assert code == cli.EXIT_OK
    assert (dest / "My_Brand_Kit").is_dir()


def test_destination_is_a_file_exits_1(run, tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")
    code, _, _ = run(str(target))
    assert code == cli.EXIT_ERROR


# --------------------------------------------------------------------------- #
# Bug #7: partial failures are reported, not swallowed
# --------------------------------------------------------------------------- #

def test_partial_failure_reports_and_exits_1(run, dest):
    (dest / "My_Brand_Kit").mkdir(parents=True)
    (dest / "My_Brand_Kit" / "01_Logos").write_text("blocking file", encoding="utf-8")

    code, out, _ = run(str(dest), "--template", "minimal", "--lang", "en")
    assert code == cli.EXIT_ERROR
    assert "Errors              : 1" in out
    # the rest of the tree is still created
    assert (dest / "My_Brand_Kit" / "02_Colors").is_dir()


# --------------------------------------------------------------------------- #
# Flags
# --------------------------------------------------------------------------- #

def test_dry_run_writes_nothing(run, dest):
    code, _, _ = run(str(dest), "--dry-run", "--template", "minimal")
    assert code == cli.EXIT_OK
    assert not dest.exists()


def test_no_samples(run, dest):
    run(str(dest), "--template", "minimal", "--no-samples", "-q")
    assert not list(dest.rglob("logo.svg"))


def test_samples_created_by_default(run, dest):
    run(str(dest), "--template", "minimal", "-q")
    assert list(dest.rglob("logo.svg"))


def test_no_manifest(run, dest):
    run(str(dest), "--template", "minimal", "--no-manifest", "-q")
    assert not (dest / "MANIFEST.md").exists()


def test_manifest_created_by_default(run, dest):
    run(str(dest), "--template", "minimal", "-q", "--brand", "Nova")
    assert "Nova" in (dest / "MANIFEST.md").read_text(encoding="utf-8")


def test_quiet_prints_nothing_on_success(run, dest):
    _, out, _ = run(str(dest), "--template", "minimal", "-q")
    assert out.strip() == ""


def test_verbose_lists_paths(run, dest):
    _, out, _ = run(str(dest), "--template", "minimal", "-v", "--lang", "en")
    assert "Directory created" in out


def test_list_templates(run):
    code, out, _ = run("--list-templates", "--lang", "en")
    assert code == cli.EXIT_OK
    for name in ("full", "minimal", "startup", "agency"):
        assert name in out


# --------------------------------------------------------------------------- #
# Language
# --------------------------------------------------------------------------- #

def test_lang_fa_output_is_rtl(run, dest):
    run(str(dest), "--template", "minimal", "--lang", "fa", "-q")
    text = (dest / "My_Brand_Kit" / "README.md").read_text(encoding="utf-8")
    assert '<div dir="rtl">' in text
    assert "## English" not in text


def test_lang_en_output_has_no_persian(run, dest):
    run(str(dest), "--template", "minimal", "--lang", "en", "-q")
    text = (dest / "My_Brand_Kit" / "README.md").read_text(encoding="utf-8")
    assert "rtl" not in text


def test_language_detection(monkeypatch):
    monkeypatch.setenv("BRANDKIT_LANG", "fa_IR.UTF-8")
    assert cli.detect_language() == "fa"
    monkeypatch.setenv("BRANDKIT_LANG", "en_US.UTF-8")
    assert cli.detect_language() == "en"
    monkeypatch.delenv("BRANDKIT_LANG")
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.setenv(var, "de_DE.UTF-8")
    assert cli.detect_language() == cli.DEFAULT_LANG


# --------------------------------------------------------------------------- #
# Brand, zip and git
# --------------------------------------------------------------------------- #

def test_brand_substitution(run, dest):
    run(str(dest), "--template", "minimal", "--brand", "Acme Corp", "-q")
    root = dest / "Acme_Corp_Brand_Kit"
    assert root.is_dir()
    assert "Acme Corp" in (root / "README.md").read_text(encoding="utf-8")


def test_zip_archive(run, dest, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run(str(dest), "--template", "minimal", "--brand", "Nova", "-z", "-q")
    archive = tmp_path / "Nova_brand_kit.zip"
    assert archive.is_file()
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    assert "MANIFEST.md" in names
    assert any(n.startswith("Nova_Brand_Kit/") for n in names)


def test_zip_custom_name(run, dest, tmp_path):
    target = tmp_path / "kit.zip"
    run(str(dest), "--template", "minimal", "-z", str(target), "-q")
    assert target.is_file()


def test_git_init(run, dest):
    pytest.importorskip("shutil")
    if cli.shutil.which("git") is None:  # pragma: no cover
        pytest.skip("git is not installed")
    run(str(dest), "--template", "minimal", "--git-init", "-q")
    assert (dest / ".git").is_dir()
    assert "filter=lfs" in (dest / ".gitattributes").read_text(encoding="utf-8")
