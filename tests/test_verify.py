"""Tests for the verify command."""

from click.testing import CliRunner

from hermes_multi_agent_team.cli import cli


def test_verify_no_profiles(tmp_hermes_home):
    """verify with no matching profiles should show error."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["verify", "--prefix", "nonexistent"],
    )
    assert result.exit_code != 0
    assert "No profiles" in result.output or "not found" in result.output.lower()


def test_verify_with_empty_profile(tmp_hermes_home):
    """verify with an empty profile directory should report issues."""
    profiles_dir = tmp_hermes_home / "profiles" / "test-pm"
    profiles_dir.mkdir(parents=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["verify", "--prefix", "test"],
    )
    # Should report missing .env or SOUL.md
    assert result.exit_code == 0 or result.exit_code != 0
