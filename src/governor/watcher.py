from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from .apply import write_operation_report
from .drift import detect_drift, recover_drift
from .paths import REPORTS_DIR
from .utils import to_jsonable


def run_once(profile: str = "ai-proxy", recover: bool = False, reload_runtime: bool = True) -> dict[str, Any]:
    if recover:
        return recover_drift(profile, reload_runtime=reload_runtime)
    return detect_drift(profile)


def watch(profile: str = "ai-proxy", interval: int = 10, recover: bool = True, reload_runtime: bool = True) -> None:
    consecutive_incomplete_recoveries = 0
    while True:
        data = run_once(profile=profile, recover=recover, reload_runtime=reload_runtime)
        write_operation_report("watcher", data, REPORTS_DIR)
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
