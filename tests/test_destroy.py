"""Tests for the destroy command."""

from click.testing import CliRunner

from hermes_multi_agent_team.cli import cli


def test_destroy_no_profiles(tmp_hermes_home):
    """destroy with no matching profiles should show error."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["destroy", "--prefix", "nonexistent"],
    )
    assert result.exit_code != 0
    assert "No profiles" in result.output or "not found" in result.output.lower()


def test_destroy_requires_confirmation(tmp_hermes_home):
    """destroy without --force should ask for confirmation."""
    # Create a fake profile
    pdir = tmp_hermes_home / "profiles" / "test-pm"
    pdir.mkdir(parents=True)
    (pdir / "SOUL.md").write_text("test")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["destroy", "--prefix", "test"],
        input="n\n",  # Decline confirmation
    )
    # Should abort
    assert result.exit_code != 0 or "Aborted" in result.output


def test_destroy_with_force(tmp_hermes_home):
    """destroy --force should delete without asking."""
    # Create fake profiles
    for role in ["pm", "fe"]:
        pdir = tmp_hermes_home / "profiles" / f"test-{role}"
        pdir.mkdir(parents=True)
        (pdir / "SOUL.md").write_text("test")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["destroy", "--prefix", "test", "--force"],
    )
    assert result.exit_code == 0
    assert "Destroyed" in result.output or "Deleted" in result.output

    # Verify they're gone
    assert not (tmp_hermes_home / "profiles" / "test-pm").exists()
    assert not (tmp_hermes_home / "profiles" / "test-fe").exists()


def test_destroy_only_deletes_matching_prefix(tmp_hermes_home):
    """destroy should only delete profiles matching the prefix."""
    # Create matching and non-matching profiles
    for name in ["test-pm", "test-fe", "other-pm"]:
        pdir = tmp_hermes_home / "profiles" / name
        pdir.mkdir(parents=True)
        (pdir / "SOUL.md").write_text("test")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["destroy", "--prefix", "test", "--force"],
    )
    assert result.exit_code == 0

    # other-pm should still exist
    assert (tmp_hermes_home / "profiles" / "other-pm").exists()
    # test-pm and test-fe should be gone
    assert not (tmp_hermes_home / "profiles" / "test-pm").exists()
    assert not (tmp_hermes_home / "profiles" / "test-fe").exists()
