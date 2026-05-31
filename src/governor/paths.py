from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"
BACKUPS_DIR = PROJECT_ROOT / "backups"
CONFIGS_GENERATED_DIR = PROJECT_ROOT / "configs" / "generated"
PROFILES_DIR = PROJECT_ROOT / "profiles"
RULES_DIR = PROJECT_ROOT / "rules"

CLASH_VERGE_DIR = Path.home() / "Library/Application Support/io.github.clash-verge-rev.clash-verge-rev"
CLASH_VERGE_CONFIG = CLASH_VERGE_DIR / "clash-verge.yaml"
CLASH_VERGE_STATE = CLASH_VERGE_DIR / "verge.yaml"
CLASH_VERGE_SERVICE_LOG = CLASH_VERGE_DIR / "logs/service/service_latest.log"
LAUNCH_AGENTS_DIR = Path.home() / "Library/LaunchAgents"
GOVERNOR_LAUNCHD_LABEL = "ai.tuxingsun.tuxs-vpn"
GOVERNOR_LAUNCHD_PLIST = LAUNCH_AGENTS_DIR / f"{GOVERNOR_LAUNCHD_LABEL}.plist"
MIHOMO_SOCKET = Path("/tmp/verge/verge-mihomo.sock")
LEGACY_INJECTOR = Path.home() / ".openclaw/tooling/bin/clash-rule-inject.py"
LEGACY_WATCHER = Path.home() / ".openclaw/tooling/bin/clash-rule-watcher.py"

DEFAULT_NETWORK_SERVICE = "Wi-Fi"
CLASH_PORTS = [7890, 7897, 7898, 7899, 9090, 9097, 57817]


@dataclass(frozen=True)
class CommandSpec:
    label: str
    args: tuple[str, ...]
    timeout: int = 8
