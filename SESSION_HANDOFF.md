# Session Handoff

## Product identity

- Full name: Tuxingsun Network Governor.
- Short code: Tuxs VPN.
- Positioning: VPN自主分流路由治理中枢.
- Long-term direction: AI 时代网络墙穿越系统.

## Current stage

The project moved from chaotic local Clash/VPN troubleshooting into GitHub public-release hardening.

## Core decisions

1. Browser usability requires system proxy enabled and Clash/mihomo `mode: rule` split routing.
2. Closing system proxy is not a valid steady state for browser domestic/foreign coexistence.
3. Durable Clash Verge governance must target active profile extensions, not only generated `clash-verge.yaml`.
4. Generated configs, backups, reports, and local runtime files must be ignored and never published.
5. The product should keep a feedback loop through usage logs, issues, and release notes.

## True source chain

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

## Current local target state

- macOS system proxy enabled to `127.0.0.1:7897`.
- mihomo runtime mode is `rule`.
- mixed port is `7897`.
- TUN disabled.
- IPv6 disabled in Clash config.
- Tuxs VPN launchd watcher label is `ai.tuxingsun.tuxs-vpn`.

## Important local paths

- Project root: `/Users/fiona/VPN`.
- Clash Verge app dir: `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev`.
- Runtime socket: `/tmp/verge/verge-mihomo.sock`.
- LaunchAgent plist: `~/Library/LaunchAgents/ai.tuxingsun.tuxs-vpn.plist`.

## Technical debt

- Browser-path A/B testing is currently script-based and should become a first-class CLI command.
- Active extension injection is operationally proven but not yet productized as a safe CLI command.
- Clean install and package build need to pass before GitHub release.
- CI needs to avoid depending on local Clash Verge state.
- README examples must stay generic and not rely on local user paths.

## Next agent priorities

1. Keep source docs aligned with actual code and target state.
2. Complete public-release packaging without publishing local runtime artifacts.
3. Add release-gate tests for no secrets and ignored artifact paths.
4. Ask for permission before git commit, push, tag, or GitHub release actions.
