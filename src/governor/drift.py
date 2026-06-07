from __future__ import annotations

from typing import Any

from .apply import apply_profile
from .clash_config import load_yaml
from .generator import expected_custom_rules
from .governance import proxy_residue_check
from .paths import CLASH_VERGE_CONFIG, CLASH_VERGE_STATE


REQUIRED_VERGE_SETTINGS = {
    "enable_system_proxy": True,
    "enable_proxy_guard": False,
    "enable_tun_mode": False,
    "enable_dns_settings": False,
}


class DriftError(RuntimeError):
    pass


def _rule_present(rules: list[Any], expected: str) -> bool:
    return any(str(rule) == expected for rule in rules)


def detect_drift(profile: str = "ai-proxy") -> dict[str, Any]:
    config = load_yaml(CLASH_VERGE_CONFIG)
    verge = load_yaml(CLASH_VERGE_STATE)
    custom_rules = expected_custom_rules(profile, config)
    rules = config.get("rules", []) or []
    missing_rules = [rule for rule in custom_rules if not _rule_present(rules, rule)]
    setting_drifts = []
    for key, expected in REQUIRED_VERGE_SETTINGS.items():
        actual = verge.get(key)
        if actual is not None and actual != expected:
            setting_drifts.append({"key": key, "expected": expected, "actual": actual})
    tun = config.get("tun") if isinstance(config.get("tun"), dict) else {}
    config_drifts = []
    if config.get("ipv6") is not False:
        config_drifts.append({"key": "ipv6", "expected": False, "actual": config.get("ipv6")})
    if tun.get("enable") is not False:
        config_drifts.append({"key": "tun.enable", "expected": False, "actual": tun.get("enable")})
    proxy = proxy_residue_check()
    drifted = bool(missing_rules or setting_drifts or config_drifts or not proxy["ok"])
    return {
        "profile": profile,
        "ok": not drifted,
        "missing_custom_rule_count": len(missing_rules),
        "missing_custom_rules_sample": missing_rules[:20],
        "verge_setting_drifts": setting_drifts,
        "config_drifts": config_drifts,
        "proxy_residue": proxy,
    }


def recover_drift(profile: str = "ai-proxy", reload_runtime: bool = True) -> dict[str, Any]:
    before = detect_drift(profile)
    if before["ok"]:
        return {"changed": False, "before": before, "after": before}
    apply_result = apply_profile(profile, reload_runtime=reload_runtime)
    after = detect_drift(profile)
    result = {"changed": True, "before": before, "apply": apply_result, "after": after}
    if not after["ok"]:
        result["recovery_incomplete"] = True
        result["recommendation"] = "stop automatic recovery and inspect true source chain"
    return result
