# Release Notes: v0.1.0-alpha

## Summary

Initial public alpha release of Tuxingsun Network Governor, product code Tuxs VPN.

Tuxs VPN is a macOS-focused local governance toolkit for Clash Verge Rev and mihomo. It helps audit, validate, recover, and document split-routing behavior across Clash Verge profile extensions, generated mihomo config, runtime rules, macOS system proxy, and launchd watcher state.

## Highlights

- CLI commands for status, audit, config, profiles, generate, apply, rollback, test, guard-proxy, drift, recover, launchd, and steady reports.
- macOS system proxy governance for browser-path split routing through `127.0.0.1:7897`.
- Clash Verge source-of-truth model covering active merge, rules, script, proxies, and groups extensions.
- mihomo Unix socket reload and runtime verification support.
- Backup and rollback support before mutable operations.
- launchd watcher under `ai.tuxingsun.tuxs-vpn`.
- Release guard for local runtime artifacts and common secret patterns.
- Public-release documentation, issue templates, CI workflow, roadmap, security policy, and usage feedback template.

## Safety notes

This release does not include proxy nodes, subscriptions, credentials, or generated local Clash/mihomo runtime configs.

Do not publish local artifacts such as:

- `backups/`
- `reports/`
- `configs/generated/`
- `clash-verge.yaml`
- `verge.yaml`
- subscriptions, tokens, passwords, private keys, or node credentials

## Verification performed

- `python3 -m build --sdist --wheel`
- clean virtualenv install from generated wheel
- `tuxs-vpn --help`
- `tuxs-vpn profiles`
- `python3 -m compileall -q src tests scripts`
- `PYTHONPATH=src python3 tests/test_mvp.py`
- `python3 scripts/release_guard.py`
- git dry-run release candidate inspection

## Known limitations

- Alpha quality.
- macOS and Clash Verge Rev focused.
- CI does not exercise local Clash Verge runtime because GitHub runners do not have the user's local Clash environment.
- Browser-path network checks depend on local node quality and upstream site behavior.
- Linux systemd and Windows scheduled task backends are not implemented.
