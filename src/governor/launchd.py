from __future__ import annotations

import plistlib
import sys
from pathlib import Path
from typing import Any

from .paths import GOVERNOR_LAUNCHD_LABEL, GOVERNOR_LAUNCHD_PLIST, LAUNCH_AGENTS_DIR, PROJECT_ROOT, REPORTS_DIR
from .utils import run_command


def plist_payload(profile: str = "ai-proxy", interval: int = 10, recover: bool = False, reload_runtime: bool = True) -> dict[str, Any]:
    args = [sys.executable, "-m", "governor.watcher", "--profile", profile, "--interval", str(interval)]
    if recover:
        args.append("--recover")
    if not reload_runtime:
        args.append("--no-reload")
    return {
        "Label": GOVERNOR_LAUNCHD_LABEL,
        "ProgramArguments": args,
        "WorkingDirectory": str(PROJECT_ROOT),
        "EnvironmentVariables": {"PYTHONPATH": str(PROJECT_ROOT / "src")},
        "RunAtLoad": True,
        "KeepAlive": False,
        "StandardOutPath": str(REPORTS_DIR / "tuxs-vpn-watcher.out.log"),
        "StandardErrorPath": str(REPORTS_DIR / "tuxs-vpn-watcher.err.log"),
    }


def write_plist(profile: str = "ai-proxy", interval: int = 10, recover: bool = False, reload_runtime: bool = True, path: Path = GOVERNOR_LAUNCHD_PLIST) -> Path:
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = plist_payload(profile=profile, interval=interval, recover=recover, reload_runtime=reload_runtime)
    with path.open("wb") as handle:
        plistlib.dump(payload, handle)
    return path


def install(profile: str = "ai-proxy", interval: int = 10, recover: bool = False, reload_runtime: bool = True) -> dict[str, Any]:
    path = write_plist(profile=profile, interval=interval, recover=recover, reload_runtime=reload_runtime)
    unload = run_command(["launchctl", "unload", str(path)])
    load = run_command(["launchctl", "load", str(path)])
    return {"plist": str(path), "unload": unload, "load": load, "status": status()}


def uninstall(path: Path = GOVERNOR_LAUNCHD_PLIST) -> dict[str, Any]:
    unload = run_command(["launchctl", "unload", str(path)]) if path.exists() else {"ok": True, "stdout": "plist missing", "stderr": ""}
    return {"plist": str(path), "unload": unload, "status": status()}


def status() -> dict[str, Any]:
    result = run_command(["sh", "-c", f"launchctl list | grep {GOVERNOR_LAUNCHD_LABEL} || true"])
    return {"label": GOVERNOR_LAUNCHD_LABEL, "plist": str(GOVERNOR_LAUNCHD_PLIST), "plist_exists": GOVERNOR_LAUNCHD_PLIST.exists(), "launchctl": result}
