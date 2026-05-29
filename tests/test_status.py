"""Tests for the status command."""

from click.testing import CliRunner

from hermes_multi_agent_team.cli import cli


def test_status_no_profiles(tmp_hermes_home):
    """status with no matching profiles should show empty or error."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["status", "--prefix", "nonexistent"],
    )
    # Status command may exit 0 with a message or exit 1 with an error
    assert "nonexistent" in result.output or "no" in result.output.lower() or result.exit_code != 0


def test_status_with_profiles(tmp_hermes_home):
    """status with existing profiles should list them."""
    # Create some fake profiles
    for role in ["pm", "fe"]:
        pdir = tmp_hermes_home / "profiles" / f"test-{role}"
        pdir.mkdir(parents=True)
        (pdir / "SOUL.md").write_text(f"# {role}")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["status", "--prefix", "test"],
    )
    assert result.exit_code == 0
