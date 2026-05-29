"""Shared fixtures for hermes-multi-agent-team tests.

CRITICAL: All tests use tmp_path to isolate from real ~/.hermes profiles.
Never test against existing profiles.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def tmp_hermes_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary HERMES_HOME directory and set the env var.

    This ensures all profile operations hit the temp dir, not the real ~/.hermes.
    """
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    profiles_dir = hermes_home / "profiles"
    profiles_dir.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    return hermes_home


@pytest.fixture()
def mock_subprocess_success(monkeypatch: pytest.MonkeyPatch):
    """Mock subprocess.run to always return success (no actual hermes calls)."""
    from subprocess import CompletedProcess

    def _fake_run(*args, **kwargs):
        return CompletedProcess(args=args[0] if args else [], returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", _fake_run)
    return _fake_run


@pytest.fixture()
def mock_subprocess_fail(monkeypatch: pytest.MonkeyPatch):
    """Mock subprocess.run to always return failure."""
    from subprocess import CompletedProcess

    def _fake_run(*args, **kwargs):
        return CompletedProcess(
            args=args[0] if args else [], returncode=1, stdout="", stderr="error"
        )

    monkeypatch.setattr("subprocess.run", _fake_run)
    return _fake_run


@pytest.fixture()
def mock_which_hermes(monkeypatch: pytest.MonkeyPatch):
    """Mock shutil.which to return a fake hermes path."""
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/local/bin/hermes" if name == "hermes" else None
    )
