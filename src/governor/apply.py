from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

from .backup import create_backup, restore_backup
from .clash_config import dump_yaml
from .generator import generate_candidate
from .paths import CLASH_VERGE_CONFIG, MIHOMO_SOCKET
from .utils import to_jsonable


class ApplyError(RuntimeError):
    pass


def _request_unix(method: str, path: str, body: str | None = None, timeout: int = 5) -> str:
    if not MIHOMO_SOCKET.exists():
        raise FileNotFoundError(str(MIHOMO_SOCKET))
    payload = body.encode() if body else b""
    request = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n".encode()
    if payload:
        request += b"Content-Type: application/json\r\nContent-Length: " + str(len(payload)).encode() + b"\r\n"
    request += b"\r\n" + payload
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect(str(MIHOMO_SOCKET))
        sock.sendall(request)
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            if len(chunk) < 65536:
                break
        return b"".join(chunks).decode(errors="replace")
    finally:
        sock.close()


def reload_mihomo(config_path: Path = CLASH_VERGE_CONFIG) -> dict[str, Any]:
    if not MIHOMO_SOCKET.exists():
        return {"attempted": False, "ok": False, "reason": "mihomo socket missing", "socket": str(MIHOMO_SOCKET)}
    payload = json.dumps({"path": str(config_path)})
    response = _request_unix("PUT", "/configs?force=true", payload)
    ok = response.startswith("HTTP/1.1 200") or response.startswith("HTTP/1.1 204") or " 200 " in response or " 204 " in response
    return {"attempted": True, "ok": ok, "response_head": response.splitlines()[:5]}


def verify_runtime_rules(keywords: list[str] | None = None) -> dict[str, Any]:
    selected = keywords or ["trae", "mchost", "github", "openai", "brave"]
    if not MIHOMO_SOCKET.exists():
        return {"attempted": False, "ok": False, "reason": "mihomo socket missing"}
    response = _request_unix("GET", "/rules")
    body = response.split("\r\n\r\n", 1)[-1]
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"attempted": True, "ok": False, "reason": "rules response is not json", "response_head": response[:200]}
    rules = data.get("rules", [])
    found = [rule for rule in rules if any(keyword in str(rule.get("payload", "")).lower() for keyword in selected)]
    return {"attempted": True, "ok": bool(found), "matched_count": len(found), "sample": found[:10]}


def apply_profile(profile: str, target: str = "mihomo", reload_runtime: bool = True, config_path: Path = CLASH_VERGE_CONFIG) -> dict[str, Any]:
    if target != "mihomo":
        raise ApplyError("apply currently supports target=mihomo only")
    backup = create_backup(f"apply profile {profile}", files=[config_path])
    candidate = generate_candidate(profile, target=target, source=config_path)
    config_path.write_text(dump_yaml(candidate), encoding="utf-8")
    reload_result = reload_mihomo(config_path) if reload_runtime else {"attempted": False, "ok": True, "reason": "reload disabled"}
    if reload_result["attempted"] and not reload_result["ok"]:
        rollback = restore_backup(Path(backup["backup_dir"]))
        raise ApplyError(json.dumps({"error": "reload failed after apply", "backup": backup, "rollback": rollback, "reload": reload_result}, ensure_ascii=False))
    rules = verify_runtime_rules() if reload_result.get("attempted") and reload_result.get("ok") else {"attempted": False, "ok": False, "reason": "runtime not reloaded"}
    return {"profile": profile, "target": target, "backup": backup, "reload": reload_result, "runtime_rules": rules}


def rollback(backup_dir: Path | None = None, reload_runtime: bool = True) -> dict[str, Any]:
    restored = restore_backup(backup_dir)
    reload_result = reload_mihomo(CLASH_VERGE_CONFIG) if reload_runtime else {"attempted": False, "ok": True, "reason": "reload disabled"}
    return {"restore": restored, "reload": reload_result}


def write_operation_report(name: str, data: dict[str, Any], reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime

    path = reports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{name}.json"
    path.write_text(json.dumps(to_jsonable(data), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
