from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .paths import CLASH_VERGE_CONFIG, LEGACY_INJECTOR
from .utils import redact

try:
    import yaml
except Exception:
    yaml = None


CLASHX_COMPATIBLE_TYPES = {"ss", "trojan", "http", "socks5"}


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read Clash YAML configs")
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def dump_yaml(data: dict[str, Any]) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML is required to write Clash YAML configs")
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)


def proxy_protocol_matrix(config: dict[str, Any]) -> dict[str, int]:
    matrix: dict[str, int] = {}
    for proxy in config.get("proxies", []) or []:
        if not isinstance(proxy, dict):
            continue
        proxy_type = str(proxy.get("type", "unknown"))
        matrix[proxy_type] = matrix.get(proxy_type, 0) + 1
    return dict(sorted(matrix.items()))


def summarize_config(path: Path = CLASH_VERGE_CONFIG) -> dict[str, Any]:
    config = load_yaml(path)
    proxies = [p for p in config.get("proxies", []) or [] if isinstance(p, dict)]
    groups = [g for g in config.get("proxy-groups", []) or [] if isinstance(g, dict)]
    rules = config.get("rules", []) or []
    compatible = [p for p in proxies if str(p.get("type")) in CLASHX_COMPATIBLE_TYPES]
    incompatible = [p for p in proxies if str(p.get("type")) not in CLASHX_COMPATIBLE_TYPES]
    dns = config.get("dns") if isinstance(config.get("dns"), dict) else {}
    tun = config.get("tun") if isinstance(config.get("tun"), dict) else {}
    return {
        "path": str(path),
        "exists": path.exists(),
        "mode": config.get("mode"),
        "mixed_port": config.get("mixed-port"),
        "external_controller_unix": config.get("external-controller-unix"),
        "ipv6": config.get("ipv6"),
        "tun_enable": tun.get("enable"),
        "dns_enable": dns.get("enable"),
        "dns_ipv6": dns.get("ipv6"),
        "dns_listen": dns.get("listen"),
        "proxy_count": len(proxies),
        "proxy_group_count": len(groups),
        "rule_count": len(rules),
        "protocol_matrix": proxy_protocol_matrix(config),
        "clashx_compatible_count": len(compatible),
        "clashx_incompatible_count": len(incompatible),
        "clashx_incompatible_types": sorted({str(p.get("type")) for p in incompatible}),
        "proxy_group_names": [str(g.get("name")) for g in groups],
        "rules_head": rules[:30],
    }


def sanitized_config(path: Path = CLASH_VERGE_CONFIG) -> dict[str, Any]:
    return redact(load_yaml(path))


def load_custom_rules_from_injector(path: Path = LEGACY_INJECTOR) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    constants: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == "PROXY_GROUP":
                constants[name] = ast.literal_eval(node.value)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id != "CUSTOM_RULES":
                continue
            rules = []
            if isinstance(node.value, ast.List):
                for item in node.value.elts:
                    if isinstance(item, ast.Constant) and isinstance(item.value, str):
                        rules.append(item.value)
                    elif isinstance(item, ast.JoinedStr):
                        text = ""
                        for part in item.values:
                            if isinstance(part, ast.Constant):
                                text += str(part.value)
                            elif isinstance(part, ast.FormattedValue) and isinstance(part.value, ast.Name):
                                text += str(constants.get(part.value.id, ""))
                        rules.append(text)
            return rules
    return []
