from __future__ import annotations

from .paths import DEFAULT_NETWORK_SERVICE
from .utils import parse_scutil_proxy, run_command


def get_proxy_state(service: str = DEFAULT_NETWORK_SERVICE) -> dict[str, object]:
    scutil = run_command(["scutil", "--proxy"])
    web = run_command(["networksetup", "-getwebproxy", service])
    secure = run_command(["networksetup", "-getsecurewebproxy", service])
    socks = run_command(["networksetup", "-getsocksfirewallproxy", service])
    return {
        "service": service,
        "scutil": parse_scutil_proxy(scutil["stdout"]),
        "http": web,
        "https": secure,
        "socks": socks,
    }
