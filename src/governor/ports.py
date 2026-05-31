from __future__ import annotations

import socket

from .paths import CLASH_PORTS


def _tcp_connectable(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def get_listening_ports(ports: list[int] | None = None) -> dict[str, object]:
    selected = ports or CLASH_PORTS
    results = {}
    for port in selected:
        results[str(port)] = {
            "listening": _tcp_connectable(port),
            "stdout": "tcp connect ok" if _tcp_connectable(port) else "",
            "stderr": "",
        }
    return {"ports": results}
