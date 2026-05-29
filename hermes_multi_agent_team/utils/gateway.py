"""Gateway helper functions for managing Feishu gateway processes."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


def get_real_home() -> Path:
    """Return the real user home directory, even if HOME is overridden by Hermes.

    In a Hermes session, HOME may point to ~/.hermes/profiles/<name>/home.
    We need the actual user home (/Users/mac or /root etc).
    """
    # Try to detect the real home by looking at /etc/passwd or known paths
    real_home = os.environ.get("REAL_HOME")
    if real_home:
        return Path(real_home)

    # If HOME looks like a hermes profile home, go up to find real home
    home = Path.home()
    parts = home.parts
    if ".hermes" in parts:
        idx = list(parts).index(".hermes")
        return Path(*parts[:idx])

    return home


def find_hermes_bin() -> str:
    """Find the hermes CLI binary.

    Priority:
    1. 'hermes' in PATH (via shutil.which)
    2. ~/.hermes/hermes-agent/venv/bin/hermes
    3. $HERMES_HOME/hermes-agent/venv/bin/hermes (if set and different)
    """
    # Try PATH first
    which_result = shutil.which("hermes")
    if which_result:
        return which_result

    # Try real home
    real_home = get_real_home()
    candidate = real_home / ".hermes" / "hermes-agent" / "venv" / "bin" / "hermes"
    if candidate.exists():
        return str(candidate)

    # Try HERMES_HOME env
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        candidate = Path(hermes_home) / "hermes-agent" / "venv" / "bin" / "hermes"
        if candidate.exists():
            return str(candidate)

    # Return the most likely path as fallback
    return str(real_home / ".hermes" / "hermes-agent" / "venv" / "bin" / "hermes")


def _hermes_bin() -> str:
    """Return the path to the hermes CLI binary."""
    return find_hermes_bin()


def gateway_status(name: str) -> dict[str, str | int | None]:
    """Check gateway status for a profile.

    Returns a dict with keys:
      - pid: process ID or None if not running
      - connected: bool — whether 'feishu connected' appears in recent logs
      - last_message_time: str or None
    """
    from hermes_multi_agent_team.utils.profile import get_profile_dir

    log_path = get_profile_dir(name) / "logs" / "gateway.log"
    result: dict[str, str | int | None] = {"pid": None, "connected": False, "last_message_time": None}

    # Find PID via pidfile or process list
    pid = _find_gateway_pid(name)
    result["pid"] = pid

    # Check connection in logs
    if log_path.exists():
        try:
            tail = _tail_file(log_path, lines=200)
            if "feishu connected" in tail.lower() or "feishu: connected" in tail.lower():
                result["connected"] = True
            # Extract last timestamp
            ts_match = re.findall(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})", tail)
            if ts_match:
                result["last_message_time"] = ts_match[-1]
        except OSError:
            pass

    return result


def _find_gateway_pid(name: str) -> int | None:
    """Try to find the running gateway PID for a profile."""
    from hermes_multi_agent_team.utils.profile import get_profile_dir

    pid_path = get_profile_dir(name) / "gateway.pid"
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            # Check if process is alive
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError, ProcessLookupError):
            pass

    # Fallback: look in process list
    try:
        out = subprocess.run(
            ["pgrep", "-f", f"hermes.*--profile.*{name}.*gateway"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return int(out.stdout.strip().split("\n")[0])
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        pass

    return None


def gateway_restart(name: str, dry_run: bool = False) -> bool:
    """Restart the gateway for a profile. Returns True on success."""
    hermes = _hermes_bin()
    cmds = [
        [hermes, "--profile", name, "gateway", "stop"],
        [hermes, "--profile", name, "gateway", "install"],
        [hermes, "--profile", name, "gateway", "start"],
    ]
    for cmd in cmds:
        if dry_run:
            print(f"  💨 dry-run: {' '.join(cmd)}")
            continue
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    return True


def get_gateway_log(name: str, tail_lines: int = 500) -> str:
    """Read the tail of the gateway log for a profile."""
    from hermes_multi_agent_team.utils.profile import get_profile_dir

    log_path = get_profile_dir(name) / "logs" / "gateway.log"
    return _tail_file(log_path, lines=tail_lines)


def _tail_file(path: Path, lines: int = 200) -> str:
    """Efficiently read the last N lines of a file."""
    if not path.exists():
        return ""
    try:
        with open(path, "rb") as f:
            # Seek to end and read backwards
            f.seek(0, 2)
            size = f.tell()
            block_size = min(size, 8192 * lines)
            f.seek(max(0, size - block_size))
            data = f.read().decode("utf-8", errors="replace")
            all_lines = data.splitlines()
            return "\n".join(all_lines[-lines:])
    except OSError:
        return ""
