# Tuxingsun Network Governor

Tuxingsun Network Governor, product code **Tuxs VPN**, is a local VPN autonomous split-routing governance center for Clash Verge Rev and mihomo on macOS.

It turns a fragile manual proxy workflow into an auditable lifecycle:

```text
Clash Verge profile extensions
  -> generated mihomo config
    -> runtime rule verification
      -> system proxy governance
        -> watcher-backed drift recovery
          -> reports and feedback loop
```

## Status

Current public baseline: `v0.1.0-alpha`.

This repository is prepared as an early open-source release. It contains governance code, profiles, tests, and documentation. It must not contain private subscriptions, proxy credentials, node passwords, raw Clash Verge runtime configs, or local backup reports.

## What it does

- Audits local Clash Verge, mihomo, macOS proxy, DNS, route, port, and VPN state.
- Generates sanitized candidate configs from local profiles.
- Applies and rolls back profile-driven config changes with backups.
- Detects routing drift, system proxy dead-port risk, IPv6/TUN drift, and missing custom rules.
- Manages a macOS launchd watcher for periodic drift recovery.
- Runs domestic, foreign, and AI/IDE connectivity checks.
- Documents the true source chain for Clash Verge profile extension governance.

## What it does not provide

- No proxy nodes.
- No subscriptions.
- No bypass guarantees.
- No hosted service.
- No private credentials or secret material.

Users must provide their own legal and authorized network environment.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
tuxs-vpn --help
tuxs-vpn status
tuxs-vpn drift --profile ai-proxy
```

For local development without installation:

```bash
PYTHONPATH=src python3 -m governor.cli status
PYTHONPATH=src python3 -m governor.cli drift --profile ai-proxy
PYTHONPATH=src python3 -m governor.cli test --skip-delay
```

## Core commands

```bash
tuxs-vpn status
tuxs-vpn audit
tuxs-vpn config
tuxs-vpn profiles
tuxs-vpn generate --profile ai-proxy --target mihomo
tuxs-vpn apply --profile ai-proxy
tuxs-vpn rollback
tuxs-vpn drift --profile ai-proxy
tuxs-vpn recover --profile ai-proxy
tuxs-vpn launchd status
tuxs-vpn steady --connectivity
```

## Lifecycle lanes

### 1. Starting archive

Use this when taking over a machine or profile for the first time.

Expected output:

- Current Clash Verge source chain.
- Runtime config summary.
- macOS proxy state.
- Drift and risk list.
- Backup and rollback point.

### 2. Periodic operations

Use this for recurring maintenance.

Expected checks:

- System proxy target state.
- `mode: rule` and mixed port health.
- Clash Verge active merge/rules/script extension stability.
- Domestic / Trae / foreign browser-path tests.
- Watcher status and drift recovery.

### 3. Incident repair

Use this when a site or tool fails.

Process:

1. Reproduce direct and proxy paths.
2. Inspect runtime rules and service logs.
3. Decide `DIRECT`, `PROXY`, or `NO_WRITE`.
4. Update durable source only after evidence.
5. Verify runtime and browser path.

## Clash Verge source-of-truth model

```text
profiles.yaml
  -> current remote profile
    -> option.merge
    -> option.script
    -> option.rules
    -> option.proxies
    -> option.groups
      -> generated clash-verge.yaml
        -> mihomo runtime /rules
```

Generated runtime config is evidence, not the only truth source. Durable governance should prefer active Clash Verge profile extensions and then verify runtime.

## Feedback and usage records

Tuxs VPN is intended to improve through field feedback. When a routing case succeeds or fails, record:

- Date and environment.
- Symptom.
- Affected domain or app.
- Direct vs proxy evidence.
- Rule or source-layer change.
- Runtime verification result.
- What should be improved in the product.

Use [USAGE_LOG_TEMPLATE.md](file:///Users/fiona/VPN/USAGE_LOG_TEMPLATE.md) for structured local notes before opening an issue or discussion.

## Safety policy

Do not commit:

- Clash Verge generated runtime configs.
- Local backups or reports.
- Proxy subscriptions.
- Proxy node hostnames with credentials.
- API keys, tokens, passwords, private keys, Authorization headers.

The `.gitignore` is intentionally strict for local runtime artifacts.

## Project state

See [CHANGELOG.md](file:///Users/fiona/VPN/CHANGELOG.md), [ROADMAP.md](file:///Users/fiona/VPN/ROADMAP.md), and [SESSION_HANDOFF.md](file:///Users/fiona/VPN/SESSION_HANDOFF.md).
