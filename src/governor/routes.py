from __future__ import annotations

from .utils import run_command


def get_route_state() -> dict[str, object]:
    return {
        "inet": run_command(["netstat", "-rn", "-f", "inet"]),
        "inet6": run_command(["netstat", "-rn", "-f", "inet6"]),
    }
