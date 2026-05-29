"""Profile helper functions for managing Hermes profiles."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


def get_hermes_home() -> Path:
    """Return the Hermes home directory (~/.hermes or $HERMES_HOME)."""
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def get_profiles_dir() -> Path:
    """Return the Hermes profiles directory."""
    return get_hermes_home() / "profiles"


def get_profile_dir(name: str) -> Path:
    """Return the directory for a specific profile."""
    return get_profiles_dir() / name


def profile_exists(name: str) -> bool:
    """Check whether a Hermes profile directory exists."""
    return get_profile_dir(name).is_dir()


def read_env(name: str) -> dict[str, str | None]:
    """Read .env from a profile directory. Returns dict of key→value (None if unset)."""
    env_path = get_profile_dir(name) / ".env"
    if not env_path.exists():
        return {}
    return dotenv_values(env_path)


def write_env(name: str, env_vars: dict[str, str]) -> None:
    """Write key=value pairs to a profile's .env file."""
    env_path = get_profile_dir(name) / ".env"
    lines: list[str] = []
    for key, value in env_vars.items():
        lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_soul(name: str) -> str:
    """Read SOUL.md from a profile directory."""
    soul_path = get_profile_dir(name) / "SOUL.md"
    if not soul_path.exists():
        return ""
    return soul_path.read_text(encoding="utf-8")


def write_soul(name: str, content: str) -> None:
    """Write content to a profile's SOUL.md file."""
    soul_path = get_profile_dir(name) / "SOUL.md"
    soul_path.write_text(content, encoding="utf-8")


def list_team_profiles(prefix: str) -> list[str]:
    """List all profile names matching the given prefix."""
    profiles_dir = get_profiles_dir()
    if not profiles_dir.is_dir():
        return []
    return sorted(
        p.name
        for p in profiles_dir.iterdir()
        if p.is_dir() and p.name.startswith(prefix)
    )
