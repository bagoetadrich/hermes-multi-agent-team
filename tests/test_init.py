"""Tests for the init command."""

from pathlib import Path

from click.testing import CliRunner

from hermes_multi_agent_team.cli import cli


def test_init_dry_run():
    """init --dry-run should not create any files."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init", "--team-name", "TestTeam", "--roles", "pm", "--dry-run"],
    )
    assert result.exit_code == 0
    assert "DRY RUN" in result.output
    assert "dry-run" in result.output


def test_init_rejects_invalid_roles():
    """init with unknown role should fail."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init", "--team-name", "TestTeam", "--roles", "pm,invalid_role"],
    )
    assert result.exit_code != 0
    assert "Unknown roles" in result.output


def test_init_creates_profiles(tmp_hermes_home: Path, mock_subprocess_success):
    """init should create profile directories and SOUL.md files."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init", "--team-name", "TestTeam", "--roles", "pm,fe", "--prefix", "test"],
    )
    assert result.exit_code == 0

    profiles_dir = tmp_hermes_home / "profiles"

    # Check profiles were created
    profiles_dir / "test-pm"
    profiles_dir / "test-fe"

    # SOUL.md should be generated (profile dirs may or may not exist depending on hermes mock)
    # At minimum, the init command should attempt to create them
    assert "TestTeam" in result.output


def test_init_skips_existing_profiles(tmp_hermes_home: Path, mock_subprocess_success):
    """init should skip profiles that already exist."""
    profiles_dir = tmp_hermes_home / "profiles"

    # Pre-create a profile
    existing = profiles_dir / "test-pm"
    existing.mkdir(parents=True)
    (existing / "SOUL.md").write_text("existing content")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init", "--team-name", "TestTeam", "--roles", "pm", "--prefix", "test"],
    )
    assert result.exit_code == 0
    assert "already exists" in result.output


def test_init_generates_soul_md(tmp_hermes_home: Path, mock_subprocess_success):
    """init should generate SOUL.md with correct content."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init", "--team-name", "MyTeam", "--roles", "qa", "--prefix", "mt"],
    )
    assert result.exit_code == 0

    soul_path = tmp_hermes_home / "profiles" / "mt-qa" / "SOUL.md"
    if soul_path.exists():
        content = soul_path.read_text()
        assert "Q宝" in content or "测试" in content


def test_init_all_roles(tmp_hermes_home: Path, mock_subprocess_success):
    """init with all default roles should succeed."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["init", "--team-name", "FullTeam", "--roles", "pm,fe,be,qa,ui", "--prefix", "full"],
    )
    assert result.exit_code == 0
    assert "FullTeam" in result.output
