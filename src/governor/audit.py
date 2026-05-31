from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .dns import get_dns_state
from .paths import (
    CLASH_VERGE_CONFIG,
    CLASH_VERGE_SERVICE_LOG,
    CLASH_VERGE_STATE,
    MIHOMO_SOCKET,
    LEGACY_INJECTOR,
    LEGACY_WATCHER,
)
from .ports import get_listening_ports
from .routes import get_route_state
from .system_proxy import get_proxy_state
from .utils import run_command
from .vpn import get_vpn_state


def collect_status() -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "paths": {
            "clash_verge_config": str(CLASH_VERGE_CONFIG),
            "clash_verge_config_exists": CLASH_VERGE_CONFIG.exists(),
            "clash_verge_state": str(CLASH_VERGE_STATE),
            "clash_verge_state_exists": CLASH_VERGE_STATE.exists(),
            "mihomo_socket": str(MIHOMO_SOCKET),
            "mihomo_socket_exists": MIHOMO_SOCKET.exists(),
            "legacy_injector": str(LEGACY_INJECTOR),
            "legacy_injector_exists": LEGACY_INJECTOR.exists(),
            "legacy_watcher": str(LEGACY_WATCHER),
            "legacy_watcher_exists": LEGACY_WATCHER.exists(),
        },
        "launchd": run_command(["sh", "-c", "launchctl list | grep -E 'tuxingsun|tuxs-vpn|clash|mihomo' || true"]),
        "system_proxy": get_proxy_state(),
        "ports": get_listening_ports(),
        "dns": get_dns_state(),
        "routes": get_route_state(),
        "vpn": get_vpn_state(),
    }


def collect_audit() -> dict[str, Any]:
    status = collect_status()
    log_text = ""
    if CLASH_VERGE_SERVICE_LOG.exists():
        log_text = CLASH_VERGE_SERVICE_LOG.read_text(encoding="utf-8", errors="ignore")
    match_lines = [line for line in log_text.splitlines() if "match Match" in line]
    failure_lines = [line for line in log_text.splitlines() if "i/o timeout" in line or "connect failed" in line]
    status["service_log_audit"] = {
        "path": str(CLASH_VERGE_SERVICE_LOG),
        "exists": CLASH_VERGE_SERVICE_LOG.exists(),
        "match_fallback_count": len(match_lines),
        "connect_failure_count": len(failure_lines),
        "match_fallback_tail": match_lines[-20:],
        "connect_failure_tail": failure_lines[-20:],
    }
    return status


def write_report(name: str, data: str, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{name}.json"
    path.write_text(data, encoding="utf-8")
    return path
