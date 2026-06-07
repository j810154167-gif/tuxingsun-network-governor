from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from .apply import write_operation_report
from .drift import detect_drift, recover_drift
from .paths import REPORTS_DIR
from .utils import to_jsonable


def _state_fingerprint(data: dict[str, Any]) -> str:
    stable = {
        "ok": data.get("ok"),
        "changed": data.get("changed"),
        "recovery_incomplete": data.get("recovery_incomplete"),
        "missing_custom_rule_count": data.get("missing_custom_rule_count"),
        "proxy_residue_ok": data.get("proxy_residue", {}).get("ok") if isinstance(data.get("proxy_residue"), dict) else None,
        "before_ok": data.get("before", {}).get("ok") if isinstance(data.get("before"), dict) else None,
        "after_ok": data.get("after", {}).get("ok") if isinstance(data.get("after"), dict) else None,
    }
    payload = json.dumps(to_jsonable(stable), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_watcher_snapshot(data: dict[str, Any], reports_dir: Path = REPORTS_DIR) -> dict[str, Any]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    latest_path = reports_dir / "watcher-latest.json"
    event_data = dict(data)
    fingerprint = _state_fingerprint(data)
    event_data["state_fingerprint"] = fingerprint

    previous_fingerprint = None
    if latest_path.exists():
        try:
            previous = json.loads(latest_path.read_text(encoding="utf-8"))
            previous_fingerprint = previous.get("state_fingerprint")
        except json.JSONDecodeError:
            previous_fingerprint = None

    latest_path.write_text(json.dumps(to_jsonable(event_data), ensure_ascii=False, indent=2), encoding="utf-8")
    changed = fingerprint != previous_fingerprint
    event_path = None
    if changed:
        event_path = write_operation_report("watcher-event", event_data, reports_dir, retain_last=100)
    return {"latest": str(latest_path), "event": str(event_path) if event_path else None, "changed": changed}


def run_once(profile: str = "ai-proxy", recover: bool = False, reload_runtime: bool = True) -> dict[str, Any]:
    if recover:
        return recover_drift(profile, reload_runtime=reload_runtime)
    return detect_drift(profile)


def watch(profile: str = "ai-proxy", interval: int = 10, recover: bool = False, reload_runtime: bool = True) -> None:
    consecutive_incomplete_recoveries = 0
    while True:
        data = run_once(profile=profile, recover=recover, reload_runtime=reload_runtime)
        write_watcher_snapshot(data, REPORTS_DIR)
        if recover and data.get("recovery_incomplete"):
            consecutive_incomplete_recoveries += 1
            if consecutive_incomplete_recoveries >= 1:
                break
        else:
            consecutive_incomplete_recoveries = 0
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tuxs-vpn-watcher")
    parser.add_argument("--profile", default="ai-proxy")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--no-reload", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.once:
        data = run_once(profile=args.profile, recover=args.recover, reload_runtime=not args.no_reload)
        print(json.dumps(to_jsonable(data), ensure_ascii=False, indent=2))
        return 0
    watch(profile=args.profile, interval=args.interval, recover=args.recover, reload_runtime=not args.no_reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
