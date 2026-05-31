from __future__ import annotations

import json
import plistlib
import subprocess
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


SENSITIVE_KEYS = {
    "password",
    "passwd",
    "uuid",
    "secret",
    "token",
    "private-key",
    "public-key",
    "short-id",
    "psk",
    "key",
}


def run_command(args: list[str] | tuple[str, ...], timeout: int = 8) -> dict[str, Any]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except FileNotFoundError as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": f"timeout after {timeout}s",
        }


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                output[key] = "<redacted>"
            else:
                output[key] = redact(item)
        return output
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(item) for item in value]
    return value


def print_json(value: Any) -> None:
    print(json.dumps(to_jsonable(value), ensure_ascii=False, indent=2, sort_keys=True))


def parse_scutil_proxy(text: str) -> dict[str, str]:
    parsed = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        parsed[key.strip()] = raw.strip()
    return parsed


def read_plist(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            value = plistlib.load(handle)
        return value if isinstance(value, dict) else {"value": value}
    except Exception as exc:
        return {"error": str(exc)}
