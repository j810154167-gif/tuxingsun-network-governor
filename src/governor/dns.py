from __future__ import annotations

from .paths import DEFAULT_NETWORK_SERVICE
from .utils import run_command


def get_dns_state(service: str = DEFAULT_NETWORK_SERVICE) -> dict[str, object]:
    return {
        "service": service,
        "networksetup": run_command(["networksetup", "-getdnsservers", service]),
        "scutil_dns_excerpt": run_command(["scutil", "--dns"], timeout=8),
    }
