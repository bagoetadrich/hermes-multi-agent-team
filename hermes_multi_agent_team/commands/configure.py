"""configure command — interactive .env configuration for team profiles."""

from __future__ import annotations


import click

from hermes_multi_agent_team.utils.profile import (
    list_team_profiles,
    read_env,
    write_env,
)

# Required .env keys and their defaults / prompt behavior
ENV_SCHEMA: list[dict[str, str | bool]] = [
    {"key": "FEISHU_APP_ID", "prompt": "Feishu App ID", "default": "", "secret": False},
    {"key": "FEISHU_APP_SECRET", "prompt": "Feishu App Secret", "default": "", "secret": True},
    {"key": "FEISHU_DOMAIN", "prompt": "Feishu Domain", "default": "feishu", "secret": False},
    {"key": "FEISHU_CONNECTION_MODE", "prompt": "Connection Mode", "default": "websocket", "secret": False},
    {"key": "FEISHU_DM_POLICY", "prompt": "DM Policy", "default": "pairing", "secret": False},
    {"key": "FEISHU_ALLOW_ALL_USERS", "prompt": "Allow All Users", "default": "false", "secret": False},
    {"key": "FEISHU_ALLOWED_USERS", "prompt": "Allowed Users (comma-separated, or empty)", "default": "", "secret": False},
    {"key": "FEISHU_ALLOW_BOTS", "prompt": "Allow Bots", "default": "all", "secret": False},
    {"key": "FEISHU_REQUIRE_MENTION", "prompt": "Require @mention", "default": "false", "secret": False},
]


def _prompt_env_vars(profile_name: str, existing: dict[str, str | None]) -> dict[str, str]:
    """Prompt the user for .env values, using existing values as defaults."""
    click.echo(f"\n  📝 Configuring .env for: {profile_name}")
    env_vars: dict[str, str] = {}

    for field in ENV_SCHEMA:
        key: str = field["key"]  # type: ignore[assignment]
        prompt_text: str = field["prompt"]  # type: ignore[assignment]
        default_val: str = field["default"]  # type: ignore[assignment]
        is_secret: bool = field["secret"]  # type: ignore[assignment]

        # Use existing value if present, otherwise use default
        current = existing.get(key) or default_val

        value = click.prompt(
            f"    {prompt_text} ({key})",
            default=current,
            hide_input=is_secret,
            show_default=not is_secret,
        )
        env_vars[key] = value

    return env_vars


def configure_team(prefix: str, dry_run: bool) -> None:
    """Interactively configure .env for each team profile."""
    profiles = list_team_profiles(prefix)

    if not profiles:
        raise click.ClickException(
            f"❌ No profiles found with prefix '{prefix}'. "
            f"Run 'hermes-team init' first."
        )

    click.echo(f"\n⚙️  Configuring {len(profiles)} profile(s) with prefix '{prefix}'")
    if dry_run:
        click.echo("   📋 DRY RUN — no changes will be made")

    # Ask if user wants to share the same Feishu app across all profiles
    share_app = click.confirm(
        "\n💡 Use the same Feishu App ID/Secret for all profiles?",
        default=True,
    )

    shared_app_id = ""
    shared_app_secret = ""

    if share_app:
        shared_app_id = click.prompt("  Feishu App ID", default="")
        shared_app_secret = click.prompt("  Feishu App Secret", default="", hide_input=True)

    success_count = 0
    for profile_name in profiles:
        existing = read_env(profile_name)

        if share_app:
            # Use shared values, prompt for the rest
            env_vars = {k: str(existing.get(k) or f["default"]) for k, f in
                        zip([f["key"] for f in ENV_SCHEMA], ENV_SCHEMA)}
            env_vars["FEISHU_APP_ID"] = shared_app_id
            env_vars["FEISHU_APP_SECRET"] = shared_app_secret
            click.echo(f"\n  📝 {profile_name}: using shared App ID/Secret")
        else:
            env_vars = _prompt_env_vars(profile_name, existing)

        if dry_run:
            click.echo(f"  💨 dry-run: would write .env for {profile_name}")
            for k, v in env_vars.items():
                display_v = "****" if "SECRET" in k else v
                click.echo(f"     {k}={display_v}")
        else:
            write_env(profile_name, env_vars)
            click.echo(f"  ✅ .env written for {profile_name}")

        success_count += 1

    click.echo(f"\n✅ Configuration complete: {success_count}/{len(profiles)} profiles configured")
    click.echo(f"\n📋 Next step: hermes-team start --prefix {prefix}")
