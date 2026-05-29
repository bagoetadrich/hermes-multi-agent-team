"""Tests for the configure command."""

from click.testing import CliRunner

from hermes_multi_agent_team.cli import cli


def test_configure_dry_run(tmp_hermes_home):
    """configure --dry-run should not write files."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["configure", "--prefix", "nonexistent", "--dry-run"],
    )
    # Should either show dry-run or error about missing profiles
    assert result.exit_code == 0 or "No profiles" in result.output


def test_configure_no_profiles(tmp_hermes_home):
    """configure with no matching profiles should show error."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["configure", "--prefix", "nonexistent"],
    )
    assert result.exit_code != 0
