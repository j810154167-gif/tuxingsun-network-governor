from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import PROFILES_DIR

try:
    import yaml
except Exception:
    yaml = None


@dataclass(frozen=True)
class Profile:
    name: str
    system_proxy: str
    tun: str
    ipv6: str
    fallback: str
    local_lan: str
    rfc1918: str
    nas: str
    docker: str
    vpn_internal: str
    trae_relay: str
    cn_sites: str
    github: str
    ai_official: str
    brave: str = "direct"
    google_api: str = "direct"
    company_internal: str = "direct"

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "Profile":
        values = {}
        for field in cls.__dataclass_fields__:
            if field == "name":
                continue
            value = data.get(field, "direct")
            if isinstance(value, bool):
                value = "on" if value else "off"
            values[field] = str(value)
        return cls(name=name, **values)


def load_profile(name: str, profiles_dir: Path = PROFILES_DIR) -> Profile:
    path = profiles_dir / f"{name}.yaml"
    if yaml is None:
        raise RuntimeError("PyYAML is required to read profiles")
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"invalid profile: {path}")
    return Profile.from_dict(name, data)


def list_profiles(profiles_dir: Path = PROFILES_DIR) -> list[str]:
    if not profiles_dir.exists():
        return []
    return sorted(path.stem for path in profiles_dir.glob("*.yaml"))
