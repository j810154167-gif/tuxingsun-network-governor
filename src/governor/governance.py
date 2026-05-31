from __future__ import annotations

from typing import Any

from .paths import DEFAULT_NETWORK_SERVICE
from .ports import get_listening_ports
from .system_proxy import get_proxy_state
from .utils import run_command


def _enabled_from_networksetup(result: dict[str, Any]) -> bool:
    return "Enabled: Yes" in str(result.get("stdout", ""))


def proxy_residue_check(service: str = DEFAULT_NETWORK_SERVICE) -> dict[str, Any]:
    state = get_proxy_state(service)
    enabled = {
        "http": _enabled_from_networksetup(state["http"]),
        "https": _enabled_from_networksetup(state["https"]),
        "socks": _enabled_from_networksetup(state["socks"]),
    }
    text = "\n".join(str(state[key].get("stdout", "")) for key in ["http", "https", "socks"])
    local_proxy_enabled = any(enabled.values()) and "127.0.0.1" in text
    ports = get_listening_ports([7897])
    mixed_port_listening = bool(ports["ports"].get("7897", {}).get("listening"))
    dead_local_port_risk = local_proxy_enabled and not mixed_port_listening
    return {
        "ok": not dead_local_port_risk,
        "enabled": enabled,
        "local_proxy_enabled": local_proxy_enabled,
        "mixed_port_listening": mixed_port_listening,
        "dead_local_port_risk": dead_local_port_risk,
        "state": state,
    }


def disable_system_proxy(service: str = DEFAULT_NETWORK_SERVICE) -> dict[str, Any]:
    commands = [
        ["networksetup", "-setwebproxystate", service, "off"],
        ["networksetup", "-setsecurewebproxystate", service, "off"],
        ["networksetup", "-setsocksfirewallproxystate", service, "off"],
    ]
    return {"commands": [run_command(command) for command in commands], "after": proxy_residue_check(service)}
