from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_PATHS = [
    ".github",
    "docs",
    "profiles",
    "rules",
    "scripts",
    "src",
    "tests",
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "RELEASE_NOTES_v0.1.0-alpha.md",
    "ROADMAP.md",
    "SECURITY.md",
    "SESSION_HANDOFF.md",
    "USAGE_LOG_TEMPLATE.md",
    "pyproject.toml",
]
FORBIDDEN_PATH_PARTS = [
    "backups/",
    "reports/",
    "configs/generated/",
    "configs/raw/",
    "profiles/raw/",
]
FORBIDDEN_NAMES = {
    "clash-verge.yaml",
    "verge.yaml",
    "config.yaml",
    "KICKOFF.md",
    "诊断修复 Clash_VPN 网络共存问题.md",
    "github发布分布组合指令.md",
}
SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization:\s*bearer\s+)[a-z0-9._\-]+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[a-z0-9._\-]{16,}"),
    re.compile(r"(?i)(token\s*[:=]\s*)[a-z0-9._\-]{16,}"),
    re.compile(r"(?i)(password\s*[:=]\s*)(?!<redacted>)[^\s]+"),
    re.compile(r"(?i)(uuid\s*[:=]\s*)(?!<redacted>)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
]
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "dist", "build", "*.egg-info"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".yaml", ".yml", ".json", ".gitignore", ".txt"}


def is_text_candidate(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {".gitignore", "LICENSE"}


def is_git_ignored(rel: str) -> bool:
    result = subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT, capture_output=True)
    return result.returncode == 0


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS or part.endswith(".egg-info") for part in path.parts)


def public_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for item in PUBLIC_PATHS:
        path = root / item
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
        else:
            files.extend(candidate for candidate in path.rglob("*") if candidate.is_file())
    return files


def scan(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    for path in public_files(root):
        rel = path.relative_to(root).as_posix()
        if should_skip(path):
            continue
        ignored = is_git_ignored(rel)
        if any(part in rel for part in FORBIDDEN_PATH_PARTS) and path.name != ".gitkeep" and not ignored:
            failures.append(f"forbidden artifact path: {rel}")
        if path.name in FORBIDDEN_NAMES and not ignored:
            failures.append(f"forbidden runtime or local-only name: {rel}")
        if is_text_candidate(path) and not ignored:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    failures.append(f"possible secret pattern in: {rel}")
                    break
    return failures


def main() -> int:
    failures = scan(ROOT)
    if failures:
        print("\n".join(failures))
        return 1
    print("release guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
