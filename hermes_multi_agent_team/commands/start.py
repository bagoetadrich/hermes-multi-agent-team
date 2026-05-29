"""start command — batch gateway install + start for all team profiles."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import click

from hermes_multi_agent_team.utils.gateway import find_hermes_bin
from hermes_multi_agent_team.utils.profile import list_team_profiles


def _run_gateway_cmd(hermes_bin: str, profile_name: str, action: str, dry_run: bool) -> bool:
    """Run a gateway command (install or start) for a profile."""
    cmd = [hermes_bin, "--profile", profile_name, "gateway", action]
    cmd_str = " ".join(cmd)

    if dry_run:
        click.echo(f"  💨 dry-run: {cmd_str}")
        return True

    click.echo(f"  🔧 {cmd_str}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return True
        else:
            click.echo(f"  ⚠️  Exit code {result.returncode}")
            if result.stderr:
                click.echo(f"     {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        click.echo(f"  ❌ Hermes binary not found: {hermes_bin}")
        return False
    except subprocess.TimeoutExpired:
        click.echo("  ❌ Command timed out")
        return False


def start_team(prefix: str, dry_run: bool) -> None:
    """Install and start the Feishu gateway for all team profiles."""
    profiles = list_team_profiles(prefix)

    if not profiles:
        raise click.ClickException(
            f"❌ No profiles found with prefix '{prefix}'. "
            f"Run 'hermes-team init' first."
        )

    hermes_bin = find_hermes_bin()

    if not Path(hermes_bin).exists() and not dry_run:
        raise click.ClickException(
            f"❌ Hermes binary not found at {hermes_bin}\n"
            f"   Please install Hermes Agent first."
        )

    click.echo(f"\n🔌 Starting gateways for {len(profiles)} profile(s)")
    if dry_run:
        click.echo("   📋 DRY RUN — no commands will be executed")
    click.echo()

    results: dict[str, bool] = {}

    for profile_name in profiles:
        click.echo(f"👤 {profile_name}")

        # Install gateway
        install_ok = _run_gateway_cmd(hermes_bin, profile_name, "install", dry_run)
        if not install_ok:
            click.echo(f"  ❌ Gateway install failed for {profile_name}")
            results[profile_name] = False
            continue

        # Start gateway
        start_ok = _run_gateway_cmd(hermes_bin, profile_name, "start", dry_run)
        if not start_ok:
            click.echo(f"  ❌ Gateway start failed for {profile_name}")
            results[profile_name] = False
            continue

        results[profile_name] = True
        click.echo(f"  ✅ Gateway started for {profile_name}")

        # Brief pause between profiles to avoid overwhelming the system
        if not dry_run:
            time.sleep(2)

    # Summary
    click.echo("\n" + "=" * 50)
    success = sum(1 for v in results.values() if v)
    failed = len(results) - success

    if failed == 0:
        click.echo(f"✅ All {success} gateways started successfully!")
    else:
        click.echo(f"✅ {success} gateway(s) started, ❌ {failed} failed")
        for name, ok in results.items():
            if not ok:
                click.echo(f"   ❌ {name}")

    click.echo()
    click.echo("📋 Next steps:")
    click.echo("   1. Wait ~30 seconds for connections to establish")
    click.echo(f"   2. hermes-team collect-ids --prefix {prefix}")
    click.echo(f"   3. hermes-team verify --prefix {prefix}")
