"""verify command — check team setup completeness."""

from __future__ import annotations

import re

import click

from hermes_multi_agent_team.utils.gateway import gateway_status
from hermes_multi_agent_team.utils.profile import (
    get_profile_dir,
    list_team_profiles,
    read_env,
    read_soul,
)

# Required .env keys
REQUIRED_ENV_KEYS = [
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
]

# Recommended .env keys
RECOMMENDED_ENV_KEYS = [
    "FEISHU_DOMAIN",
    "FEISHU_CONNECTION_MODE",
    "FEISHU_DM_POLICY",
    "FEISHU_ALLOW_ALL_USERS",
    "FEISHU_ALLOW_BOTS",
    "FEISHU_REQUIRE_MENTION",
]


def _check_profile(profile_name: str) -> dict[str, tuple[bool, str]]:
    """Run all checks for a single profile. Returns check_name → (pass, detail)."""
    checks: dict[str, tuple[bool, str]] = {}

    # 1. Profile directory exists
    profile_dir = get_profile_dir(profile_name)
    checks["profile_dir"] = (
        profile_dir.is_dir(),
        str(profile_dir),
    )

    # 2. .env exists and has required keys
    env = read_env(profile_name)
    env_exists = bool(env)
    missing_required = [k for k in REQUIRED_ENV_KEYS if not env.get(k)]
    missing_recommended = [k for k in RECOMMENDED_ENV_KEYS if not env.get(k)]

    if not env_exists:
        checks["env_file"] = (False, ".env not found")
    elif missing_required:
        checks["env_file"] = (False, f"missing required: {', '.join(missing_required)}")
    else:
        checks["env_file"] = (True, "OK")

    if missing_recommended:
        checks["env_recommended"] = (
            False,
            f"missing recommended: {', '.join(missing_recommended)}",
        )
    else:
        checks["env_recommended"] = (True, "OK")

    # 3. SOUL.md exists
    soul = read_soul(profile_name)
    checks["soul_md"] = (bool(soul), "OK" if soul else "SOUL.md not found or empty")

    # 4. SOUL.md has real open_ids (not placeholders)
    if soul:
        placeholder_pattern = re.compile(r'user_id="ou_xxx[^"]*"')
        has_placeholders = bool(placeholder_pattern.search(soul))
        real_id_pattern = re.compile(r'user_id="(ou_[a-zA-Z0-9]+)"')
        real_ids = set(real_id_pattern.findall(soul)) - {
            "ou_xxx_pm",
            "ou_xxx_fe",
            "ou_xxx_be",
            "ou_xxx_qa",
            "ou_xxx_ui",
        }

        if has_placeholders and not real_ids:
            checks["open_ids"] = (False, "SOUL.md still has placeholder open_ids")
        elif real_ids:
            checks["open_ids"] = (True, f"found {len(real_ids)} open_id(s)")
        else:
            checks["open_ids"] = (False, "no open_ids found in SOUL.md")
    else:
        checks["open_ids"] = (False, "no SOUL.md")

    # 5. Gateway connection
    gw = gateway_status(profile_name)
    pid = gw["pid"]
    connected = gw["connected"]

    if pid:
        checks["gateway_running"] = (True, f"PID {pid}")
    else:
        checks["gateway_running"] = (False, "not running")

    if connected:
        checks["gateway_connected"] = (True, "feishu connected")
    else:
        checks["gateway_connected"] = (False, "not connected")

    return checks


def verify_team(prefix: str) -> None:
    """Verify team setup: gateways, .env, SOUL.md open_ids."""
    profiles = list_team_profiles(prefix)

    if not profiles:
        raise click.ClickException(
            f"❌ No profiles found with prefix '{prefix}'. Run 'hermes-team init' first."
        )

    click.echo(f"\n✅ Verifying {len(profiles)} profile(s) with prefix '{prefix}'\n")

    all_pass = True
    profile_results: dict[str, dict[str, tuple[bool, str]]] = {}

    for profile_name in profiles:
        results = _check_profile(profile_name)
        profile_results[profile_name] = results

        profile_pass = all(ok for ok, _ in results.values())
        if not profile_pass:
            all_pass = False

        # Display results
        status_icon = "✅" if profile_pass else "❌"
        click.echo(f"{status_icon} {profile_name}")

        for check_name, (ok, detail) in results.items():
            icon = "✅" if ok else "❌"
            click.echo(f"   {icon} {check_name}: {detail}")
        click.echo()

    # Summary
    click.echo("=" * 60)
    if all_pass:
        click.echo("🎉 ALL CHECKS PASSED! Your team is ready to go!")
    else:
        failed_profiles = [
            name
            for name, checks in profile_results.items()
            if not all(ok for ok, _ in checks.values())
        ]
        click.echo(f"⚠️  Some checks failed for: {', '.join(failed_profiles)}")
        click.echo()
        click.echo("🔧 Common fixes:")
        click.echo("   - Missing .env: hermes-team configure --prefix " + prefix)
        click.echo("   - No open_ids: hermes-team collect-ids --prefix " + prefix)
        click.echo("   - Gateway not running: hermes-team start --prefix " + prefix)
