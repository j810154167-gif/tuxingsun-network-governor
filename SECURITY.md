# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x-alpha | Best-effort security fixes |

## Reporting a vulnerability

Please report security issues privately before public disclosure.

Preferred channel: create a private security advisory on GitHub once the repository is public.

If private advisory is unavailable, contact the maintainer through the repository owner profile and avoid including secrets in public issues.

## Sensitive data policy

This project must not receive or publish:

- Proxy subscriptions.
- Proxy node credentials.
- API keys or provider tokens.
- Passwords or private keys.
- Authorization headers or cookies.
- Full unredacted Clash Verge configs.
- Local backup or runtime report archives.

## Known risk areas

- Local network state can reveal machine-specific paths and service names.
- Generated Clash/mihomo configs can include proxy endpoints and credentials.
- Runtime logs can include domains or private application usage patterns.
- Automated rule writing can break connectivity if not verified through runtime evidence.

## Maintainer expectations

- Redact before sharing logs or configs.
- Prefer minimal reproductions over full runtime dumps.
- Add release gates for any new artifact path that may contain secrets.
