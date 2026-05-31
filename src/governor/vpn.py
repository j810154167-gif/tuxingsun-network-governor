from __future__ import annotations

from .utils import run_command


def get_vpn_state() -> dict[str, object]:
    return {
        "utun": run_command(["sh", "-c", "ifconfig 2>/dev/null | awk '/^utun/{print $1}'"], timeout=8),
        "utun_detail": run_command(["sh", "-c", "ifconfig utun* 2>/dev/null"], timeout=8),
    }
