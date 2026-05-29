"""Tests for the doctor command."""

from click.testing import CliRunner

from hermes_multi_agent_team.cli import cli


def test_doctor_runs():
    """doctor should run without crashing."""
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0
    assert "doctor" in result.output.lower() or "check" in result.output.lower()


def test_doctor_shows_python_check():
    """doctor should check Python version."""
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert "Python" in result.output or "python" in result.output


def test_doctor_shows_hermes_check():
    """doctor should check for Hermes CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    # Should mention Hermes in output
    assert "Hermes" in result.output or "hermes" in result.output
