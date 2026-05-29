"""destroy command — remove team profiles safely."""

from __future__ import annotations

import shutil

import click

from hermes_multi_agent_team.utils.profile import get_profiles_dir, list_team_profiles


def destroy_team(prefix: str, force: bool) -> None:
    """List matching team profiles, confirm, and delete them."""
    profiles = list_team_profiles(prefix)

    if not profiles:
        raise click.ClickException(
            f"❌ No profiles found with prefix '{prefix}'. Nothing to destroy."
        )

    profiles_dir = get_profiles_dir()

    click.echo(f"\n🗑️  Destroy Team Profiles — prefix: '{prefix}'")
    click.echo(f"   Found {len(profiles)} profile(s):\n")

    for name in profiles:
        pdir = profiles_dir / name
        # Show a rough size hint
        file_count = sum(1 for _ in pdir.rglob("*") if _.is_file()) if pdir.is_dir() else 0
        click.echo(f"   • {name}  ({file_count} files)")

    click.echo()

    # Safety: confirm unless --force
    if not force:
        click.confirm(
            f"⚠️  This will permanently delete {len(profiles)} profile(s). Continue?",
            abort=True,
        )

    # Delete
    deleted = []
    for name in profiles:
        pdir = profiles_dir / name
        if pdir.is_dir():
            shutil.rmtree(pdir)
            deleted.append(name)
            click.echo(f"   🗑️  Deleted: {name}")

    click.echo()
    click.echo(f"✅ Destroyed {len(deleted)} profile(s): {', '.join(deleted)}")
    click.echo()
