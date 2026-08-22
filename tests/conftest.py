"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brand_kit_generator import cli


@pytest.fixture()
def run(tmp_path, monkeypatch, capsys):
    """Run the CLI and return (exit_code, stdout, stderr)."""

    def _run(*args: str, stdin: str | None = None):
        if stdin is not None:
            monkeypatch.setattr("builtins.input", lambda *_: stdin)
        code = cli.main(list(args))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


@pytest.fixture()
def dest(tmp_path) -> Path:
    return tmp_path / "dest"
