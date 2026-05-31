from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .apply import apply_profile, rollback, write_operation_report
from .audit import collect_audit, collect_status, write_report
from .clash_config import summarize_config
from .drift import detect_drift, recover_drift
from .generator import write_candidate
from .governance import disable_system_proxy, proxy_residue_check
from .launchd import install as launchd_install, status as launchd_status, uninstall as launchd_uninstall, write_plist
from .paths import CLASH_VERGE_CONFIG, REPORTS_DIR
from .profiles import list_profiles, load_profile
from .report import write_steady_report
from .test_runner import batch_connectivity, mihomo_delay
from .utils import print_json, to_jsonable


def cmd_status(args: argparse.Namespace) -> int:
    data = collect_status()
    if args.write_report:
        path = write_report("status", json.dumps(to_jsonable(data), ensure_ascii=False, indent=2), REPORTS_DIR)
        print(path)
    else:
        print_json(data)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    data = collect_audit()
    data["clash_config_summary"] = summarize_config()
    if args.write_report:
        path = write_report("audit", json.dumps(to_jsonable(data), ensure_ascii=False, indent=2), REPORTS_DIR)
        print(path)
    else:
        print_json(data)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    path = write_candidate(args.profile, target=args.target)
    print(path)
    return 0


def cmd_profiles(args: argparse.Namespace) -> int:
    if args.profile:
        print_json(load_profile(args.profile))
    else:
        print_json({"profiles": list_profiles()})
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    path = Path(args.path) if args.path else CLASH_VERGE_CONFIG
    print_json(summarize_config(path))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    data = apply_profile(args.profile, target=args.target, reload_runtime=not args.no_reload)
    report = write_operation_report("apply", data, REPORTS_DIR)
    print_json({"report": str(report), "result": data})
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    backup_dir = Path(args.backup_dir) if args.backup_dir else None
    data = rollback(backup_dir=backup_dir, reload_runtime=not args.no_reload)
    report = write_operation_report("rollback", data, REPORTS_DIR)
    print_json({"report": str(report), "result": data})
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    data = {
        "proxy_residue": proxy_residue_check(),
        "status": collect_status(),
        "connectivity": batch_connectivity(timeout=args.timeout) if not args.skip_connectivity else {"skipped": True},
        "delay": mihomo_delay(limit=args.delay_limit) if not args.skip_delay else {"skipped": True},
    }
    report = write_operation_report("test", data, REPORTS_DIR)
    print_json({"report": str(report), "result": data})
    return 0


def cmd_guard_proxy(args: argparse.Namespace) -> int:
    data = disable_system_proxy() if args.fix else proxy_residue_check()
    print_json(data)
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    print_json(detect_drift(args.profile))
    return 0


def cmd_recover(args: argparse.Namespace) -> int:
    data = recover_drift(args.profile, reload_runtime=not args.no_reload)
    report = write_operation_report("recover", data, REPORTS_DIR)
    print_json({"report": str(report), "result": data})
    return 0


def cmd_launchd(args: argparse.Namespace) -> int:
    if args.action == "write":
        path = write_plist(profile=args.profile, interval=args.interval, recover=not args.no_recover, reload_runtime=not args.no_reload)
        print_json({"plist": str(path)})
    elif args.action == "install":
        print_json(launchd_install(profile=args.profile, interval=args.interval, recover=not args.no_recover, reload_runtime=not args.no_reload))
    elif args.action == "uninstall":
        print_json(launchd_uninstall())
    else:
        print_json(launchd_status())
    return 0


def cmd_steady(args: argparse.Namespace) -> int:
    path = write_steady_report(run_connectivity=args.connectivity, run_delay=args.delay)
    print(path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tuxs-vpn", description="Tuxingsun Network Governor - VPN自主分流路由治理中枢")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--write-report", action="store_true")
    status.set_defaults(func=cmd_status)

    audit = sub.add_parser("audit")
    audit.add_argument("--write-report", action="store_true")
    audit.set_defaults(func=cmd_audit)

    generate = sub.add_parser("generate")
    generate.add_argument("--profile", required=True)
    generate.add_argument("--target", choices=["mihomo", "clashx"], default="mihomo")
    generate.set_defaults(func=cmd_generate)

    profiles = sub.add_parser("profiles")
    profiles.add_argument("profile", nargs="?")
    profiles.set_defaults(func=cmd_profiles)

    config = sub.add_parser("config")
    config.add_argument("--path")
    config.set_defaults(func=cmd_config)

    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("--profile", required=True)
    apply_parser.add_argument("--target", choices=["mihomo"], default="mihomo")
    apply_parser.add_argument("--no-reload", action="store_true")
    apply_parser.set_defaults(func=cmd_apply)

    rollback_parser = sub.add_parser("rollback")
    rollback_parser.add_argument("--backup-dir")
    rollback_parser.add_argument("--no-reload", action="store_true")
    rollback_parser.set_defaults(func=cmd_rollback)

    test = sub.add_parser("test")
    test.add_argument("--timeout", type=int, default=8)
    test.add_argument("--delay-limit", type=int, default=20)
    test.add_argument("--skip-connectivity", action="store_true")
    test.add_argument("--skip-delay", action="store_true")
    test.set_defaults(func=cmd_test)

    guard = sub.add_parser("guard-proxy")
    guard.add_argument("--fix", action="store_true")
    guard.set_defaults(func=cmd_guard_proxy)

    drift = sub.add_parser("drift")
    drift.add_argument("--profile", default="ai-proxy")
    drift.set_defaults(func=cmd_drift)

    recover = sub.add_parser("recover")
    recover.add_argument("--profile", default="ai-proxy")
    recover.add_argument("--no-reload", action="store_true")
    recover.set_defaults(func=cmd_recover)

    launchd = sub.add_parser("launchd")
    launchd.add_argument("action", choices=["write", "install", "uninstall", "status"])
    launchd.add_argument("--profile", default="ai-proxy")
    launchd.add_argument("--interval", type=int, default=10)
    launchd.add_argument("--no-recover", action="store_true")
    launchd.add_argument("--no-reload", action="store_true")
    launchd.set_defaults(func=cmd_launchd)

    steady = sub.add_parser("steady")
    steady.add_argument("--connectivity", action="store_true")
    steady.add_argument("--delay", action="store_true")
    steady.set_defaults(func=cmd_steady)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
