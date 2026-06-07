from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .clash_config import CLASHX_COMPATIBLE_TYPES, dump_yaml, load_custom_rules_from_injector, load_yaml
from .paths import CLASH_VERGE_CONFIG, CONFIGS_GENERATED_DIR
from .profiles import Profile, load_profile
from .utils import redact


PROFILE_PROXY_FIELDS = {"github", "ai_official", "brave", "google_api"}


def _proxy_group_name(config: dict[str, Any]) -> str:
    groups = [g for g in config.get("proxy-groups", []) or [] if isinstance(g, dict)]
    for group in groups:
        name = str(group.get("name", ""))
        if "国外" in name or "proxy" in name.lower():
            return name
    return str(groups[0].get("name", "PROXY")) if groups else "PROXY"


def _rewrite_profile_rules(rules: list[str], profile: Profile, proxy_group: str) -> list[str]:
    if any(getattr(profile, field) == "proxy" for field in PROFILE_PROXY_FIELDS):
        return [rule.replace("🔰国外流量", proxy_group) for rule in rules]
    rewritten = []
    for rule in rules:
        if "🔰国外流量" in rule or rule.endswith(f",{proxy_group}"):
            parts = rule.split(",")
            if len(parts) >= 3:
                parts[-1] = "DIRECT"
                rewritten.append(",".join(parts))
                continue
        rewritten.append(rule)
    return rewritten


def expected_custom_rules(profile_name: str, config: dict[str, Any]) -> list[str]:
    profile = load_profile(profile_name)
    proxy_group = _proxy_group_name(config)
    return _rewrite_profile_rules(load_custom_rules_from_injector(), profile, proxy_group)


def _filter_clashx(config: dict[str, Any]) -> dict[str, Any]:
    output = deepcopy(config)
    proxies = [p for p in output.get("proxies", []) or [] if isinstance(p, dict) and str(p.get("type")) in CLASHX_COMPATIBLE_TYPES]
    names = {str(p.get("name")) for p in proxies}
    output["proxies"] = proxies
    groups = []
    for group in output.get("proxy-groups", []) or []:
        if not isinstance(group, dict):
            continue
        copied = deepcopy(group)
        copied["proxies"] = [name for name in copied.get("proxies", []) or [] if name in names or name == "DIRECT"]
        if not copied["proxies"]:
            copied["proxies"] = ["DIRECT"]
        groups.append(copied)
    output["proxy-groups"] = groups
    return output


def generate_candidate(profile_name: str, target: str = "mihomo", source: Path = CLASH_VERGE_CONFIG) -> dict[str, Any]:
    profile = load_profile(profile_name)
    config = load_yaml(source)
    output = deepcopy(config)
    output["ipv6"] = profile.ipv6 == "on"
    tun = output.get("tun") if isinstance(output.get("tun"), dict) else {}
    tun["enable"] = profile.tun == "on"
    output["tun"] = tun
    custom_rules = expected_custom_rules(profile_name, output)
    existing_rules = [rule for rule in output.get("rules", []) or [] if rule not in custom_rules]
    output["rules"] = custom_rules + existing_rules
    if target == "clashx":
        output = _filter_clashx(output)
    return output


def write_candidate(profile_name: str, target: str = "mihomo", output_dir: Path = CONFIGS_GENERATED_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = generate_candidate(profile_name, target=target)
    path = output_dir / f"{profile_name}.{target}.yaml"
    path.write_text(dump_yaml(redact(config)), encoding="utf-8")
    return path
