from __future__ import annotations

from pathlib import Path

from governor.apply import apply_profile, rollback
from governor.clash_config import summarize_config
from governor.drift import detect_drift
from governor.generator import generate_candidate, write_candidate
from governor.governance import proxy_residue_check
from governor.launchd import plist_payload, status
from governor.profiles import list_profiles, load_profile
from governor.release_guard import scan
from governor.report import steady_report
from governor.watcher import run_once, watch


def test_profiles_load() -> None:
    names = list_profiles()
    assert {"clean-direct", "ai-proxy", "vpn-compatible"}.issubset(set(names))
    profile = load_profile("ai-proxy")
    assert profile.github == "proxy"
    assert profile.system_proxy == "on"


def test_config_summary_has_protocol_matrix() -> None:
    summary = summarize_config()
    assert summary["exists"] is True
    assert summary["proxy_count"] >= 0
    assert isinstance(summary["protocol_matrix"], dict)


def test_generate_candidate_is_sanitizable() -> None:
    config = generate_candidate("ai-proxy", target="clashx")
    assert config["ipv6"] is False
    assert config["tun"]["enable"] is False
    assert all(proxy.get("type") in {"ss", "trojan", "http", "socks5"} for proxy in config.get("proxies", []))


def test_regenerate_candidate_is_idempotent(tmp_path: Path) -> None:
    output_dir = tmp_path / "generated"
    first = write_candidate("ai-proxy", target="mihomo", output_dir=output_dir)
    first_text = first.read_text(encoding="utf-8")
    second = write_candidate("ai-proxy", target="mihomo", output_dir=output_dir)
    second_text = second.read_text(encoding="utf-8")
    assert first == second
    assert first_text == second_text
    assert "password: <redacted>" in second_text.lower()
    assert "uuid: <redacted>" in second_text.lower()


def test_apply_no_reload_creates_backup_and_rollback_restores(tmp_path: Path) -> None:
    config_path = tmp_path / "clash-verge.yaml"
    backups_dir = tmp_path / "backups"
    config_path.write_text("mode: rule\nproxies: []\nproxy-groups: []\nrules: []\n", encoding="utf-8")
    result = apply_profile("clean-direct", reload_runtime=False, config_path=config_path, backups_dir=backups_dir)
    backup_dir = Path(result["backup"]["backup_dir"])
    assert backup_dir.exists()
    assert (backup_dir / "manifest.json").exists()
    restored = rollback(backup_dir=backup_dir, reload_runtime=False)
    assert restored["restore"]["backup_dir"] == str(backup_dir)
    assert any(item["restored"] for item in restored["restore"]["restored"])


def test_proxy_residue_check_shape() -> None:
    result = proxy_residue_check()
    assert "ok" in result
    assert "dead_local_port_risk" in result
    assert "enabled" in result


def test_drift_report_shape() -> None:
    result = detect_drift("ai-proxy")
    assert "ok" in result
    assert "missing_custom_rule_count" in result
    assert "proxy_residue" in result


def test_ai_proxy_candidate_satisfies_custom_rule_drift() -> None:
    config = generate_candidate("ai-proxy", target="mihomo")
    rules = config.get("rules", [])
    assert any("github.com" in str(rule) for rule in rules)
    assert all("🔰国外流量" not in str(rule) for rule in rules)


def test_watcher_run_once_reports_recovery_result() -> None:
    result = run_once(profile="ai-proxy", recover=False, reload_runtime=False)
    assert "ok" in result


def test_launchd_payload_shape() -> None:
    payload = plist_payload(profile="ai-proxy", interval=30, recover=True, reload_runtime=False)
    assert payload["Label"] == "ai.tuxingsun.tuxs-vpn"
    assert "--recover" in payload["ProgramArguments"]
    assert "--no-reload" in payload["ProgramArguments"]
    assert payload["EnvironmentVariables"]["PYTHONPATH"].endswith("src")


def test_launchd_default_is_observe_only() -> None:
    payload = plist_payload(profile="ai-proxy", interval=30)
    assert "--recover" not in payload["ProgramArguments"]
    assert payload["KeepAlive"] is False


def test_launchd_status_reports_legacy_conflicts() -> None:
    result = status()
    assert any(item["label"] == "ai.openclaw.network-governor" for item in result["conflicts"])


def test_watcher_default_is_observe_only() -> None:
    assert watch.__defaults__[2] is False


def test_release_guard_has_no_publication_blockers() -> None:
    assert scan() == []


def test_steady_report_shape() -> None:
    result = steady_report(run_connectivity=False, run_delay=False)
    assert result["connectivity"] == {"skipped": True}
    assert result["delay"] == {"skipped": True}
    assert result["risks"]
    assert result["usage"]
