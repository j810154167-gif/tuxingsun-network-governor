# Changelog

All notable changes to Tuxingsun Network Governor are documented here.

The format follows Keep a Changelog and this project uses semantic versioning where practical.

## [0.1.0-alpha] - 2026-05-31

### Added

- Initial Tuxs VPN governance CLI with status, audit, config, profiles, generate, apply, rollback, test, guard-proxy, drift, recover, launchd, and steady commands.
- macOS Clash Verge Rev and mihomo runtime inspection.
- Profile-driven config generation for mihomo and ClashX-compatible outputs.
- Backup and rollback before mutable operations.
- mihomo Unix socket reload and runtime verification support.
- Drift detection for system proxy, IPv6, TUN, custom rules, and dead local proxy port risk.
- launchd watcher generation and management under `ai.tuxingsun.tuxs-vpn`.
- Active Clash Verge source-of-truth model for merge, rules, script, proxies, and groups extensions.
- Browser-path split-routing validation for domestic, Trae, and foreign sites.
- Product identity: Tuxingsun Network Governor / Tuxs VPN / VPN自主分流路由治理中枢.

### Changed

- Switched steady target state to system proxy enabled with `mode: rule` split routing.
- Replaced port liveness checks with TCP connect checks to avoid `lsof` false negatives.
- Rebranded public-facing project metadata from legacy internal naming to Tuxingsun/Tuxs.

### Security

- Added strict ignore rules for backups, reports, generated configs, raw configs, subscriptions, tokens, passwords, keys, and mobileconfig files.
- Redaction is required for generated candidate configs and reports before public sharing.

### Known limitations

- First public release is macOS and Clash Verge Rev focused.
- Linux systemd and Windows Task Scheduler are not implemented.
- GitHub release automation is not yet wired.
- Network batch tests may vary by local node quality and upstream site behavior.
