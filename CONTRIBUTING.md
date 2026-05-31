# Contributing

Thank you for considering a contribution to Tuxingsun Network Governor.

## Development setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
python3 -m compileall -q src tests
PYTHONPATH=src python3 tests/test_mvp.py
```

## Safety rules

Never commit:

- Proxy subscriptions.
- Proxy node credentials.
- Clash Verge generated runtime configs.
- Local backup directories.
- Runtime reports that include local machine details.
- API tokens, passwords, private keys, Authorization headers, or cookies.

Run before opening a pull request:

```bash
git add -n .
git status --short --ignored
```

## Commit style

Use Conventional Commits:

```text
feat: add profile extension scanner
fix: repair dead-port risk detection
docs: add source-of-truth model
test: add browser-path split routing acceptance
chore: prepare public release metadata
```

## Pull request checklist

- [ ] The change has a clear use case.
- [ ] Local tests pass.
- [ ] No sensitive local artifacts are included.
- [ ] README or docs are updated if behavior changes.
- [ ] Rollback or recovery behavior is considered for mutable operations.
