"""doctor command — check environment dependencies and readiness."""

from __future__ import annotations

import shutil
import sys

import click


def _check_python_version() -> tuple[bool, str, str]:
    """Check Python >= 3.10."""
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 10)
    detail = f"{major}.{minor}.{sys.version_info[2]}"
    if ok:
        return ok, detail, ""
    return ok, detail, "Please upgrade to Python 3.10+"


def _check_hermes_installed() -> tuple[bool, str, str]:
    """Check if Hermes Agent CLI is available."""
    hermes_path = shutil.which("hermes")
    if hermes_path:
        return True, hermes_path, ""
    return False, "not found", "Install: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"


def _check_click() -> tuple[bool, str, str]:
    """Check click package."""
    try:
        import importlib.metadata
        ver = importlib.metadata.version("click")
        return True, ver, ""
    except (ImportError, importlib.metadata.PackageNotFoundError):
        return False, "not installed", "pip install click>=8.0"


def _check_dotenv() -> tuple[bool, str, str]:
    """Check python-dotenv package."""
    try:
        import importlib.metadata
        ver = importlib.metadata.version("python-dotenv")
        return True, ver, ""
    except (ImportError, importlib.metadata.PackageNotFoundError):
        return False, "not installed", "pip install python-dotenv>=1.0"


def _check_jinja2() -> tuple[bool, str, str]:
    """Check Jinja2 package."""
    try:
        import jinja2
        return True, jinja2.__version__, ""
    except ImportError:
        return False, "not installed", "pip install jinja2>=3.0"


def _check_hermes_profiles_dir() -> tuple[bool, str, str]:
    """Check if ~/.hermes/profiles directory exists."""
    from hermes_multi_agent_team.utils.profile import get_profiles_dir

    profiles_dir = get_profiles_dir()
    if profiles_dir.is_dir():
        return True, str(profiles_dir), ""
    return False, "not found", f"mkdir -p {profiles_dir}"


ALL_CHECKS = [
    ("Python ≥3.10", _check_python_version),
    ("Hermes CLI", _check_hermes_installed),
    ("click", _check_click),
    ("python-dotenv", _check_dotenv),
    ("Jinja2", _check_jinja2),
    ("Profiles dir", _check_hermes_profiles_dir),
]


def run_doctor() -> None:
    """Check environment dependencies and print a status table."""
    click.echo()
    click.echo("🩺 hermes-team doctor — Environment Health Check")
    click.echo("=" * 60)
    click.echo()

    all_ok = True
    results: list[tuple[str, bool, str, str]] = []

    for label, check_fn in ALL_CHECKS:
        ok, detail, fix = check_fn()
        if not ok:
            all_ok = False
        results.append((label, ok, detail, fix))

    # Table
    click.echo(f"   {'Check':<20} {'Status':<8} {'Detail':<30}")
    click.echo("   " + "─" * 58)

    for label, ok, detail, _fix in results:
        icon = "✅" if ok else "❌"
        click.echo(f"   {label:<20} {icon:<8} {detail:<30}")

    click.echo("   " + "─" * 58)
    click.echo()

    # Summary
    passed = sum(1 for _, ok, _, _ in results if ok)
    total = len(results)

    if all_ok:
        click.echo(f"🎉 All {total} checks passed! Environment is ready.")
    else:
        click.echo(f"⚠️  {passed}/{total} checks passed. Fix the issues below:\n")
        for label, ok, _detail, fix in results:
            if not ok and fix:
                click.echo(f"   ❌ {label}: {fix}")
        click.echo()

    click.echo("💡 Quick commands:")
    click.echo("   hermes-team init --team-name my-team   # Create a team")
    click.echo("   hermes-team status --prefix my-team    # Check team status")
    click.echo()
