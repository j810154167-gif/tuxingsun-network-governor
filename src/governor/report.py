from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .audit import collect_audit
from .clash_config import summarize_config
from .drift import detect_drift
from .governance import proxy_residue_check
from .launchd import status as launchd_status
from .paths import REPORTS_DIR
from .test_runner import batch_connectivity, mihomo_delay
from .utils import to_jsonable


RISK_ITEMS = [
    {"risk": "mihomo 未启动时无法验证运行时 /rules 与节点 delay", "mitigation": "启动 Clash Verge 后运行 Tuxs VPN test；写入修复必须单独授权"},
    {"risk": "Clash Verge GUI 可能重写 clash-verge.yaml 或 verge.yaml", "mitigation": "watcher 默认只观测漂移；修复真源链后再授权 apply"},
    {"risk": "生成配置可能包含订阅节点字段", "mitigation": "configs/generated 已被 .gitignore 排除，报告只写摘要"},
    {"risk": "系统代理被其他 GUI 打开后指向本地死端口", "mitigation": "guard-proxy 只读检测；修复系统代理必须单独授权"},
    {"risk": "ClashX 仅兼容 ss/trojan 等部分节点", "mitigation": "ClashX 作为备用层，不作为 mihomo 完整替代"},
]


PRODUCT_IDENTITY = {
    "full_name": "Tuxingsun Network Governor",
    "short_code": "Tuxs VPN",
    "positioning": "VPN自主分流路由治理中枢",
    "rd_direction": "AI 时代网络墙穿越系统",
}


USAGE_LINES = [
    "PYTHONPATH=src python3 -m governor.cli status --write-report",
    "PYTHONPATH=src python3 -m governor.cli audit --write-report",
    "PYTHONPATH=src python3 -m governor.cli generate --profile ai-proxy --target mihomo",
    "PYTHONPATH=src python3 -m governor.cli apply --profile ai-proxy",
    "PYTHONPATH=src python3 -m governor.cli rollback",
    "PYTHONPATH=src python3 -m governor.cli test",
    "PYTHONPATH=src python3 -m governor.cli drift --profile ai-proxy",
    "PYTHONPATH=src python3 -m governor.cli recover --profile ai-proxy",
    "PYTHONPATH=src python3 -m governor.cli launchd write --profile ai-proxy",
    "PYTHONPATH=src python3 -m governor.cli launchd install --profile ai-proxy",
    "PYTHONPATH=src python3 -m governor.cli launchd status",
]


GUI_ROUTE = [
    "保留 Tuxingsun Network Governor CLI 作为网络主权层",
    "GUI 只调用 status/audit/apply/rollback/test/drift/recover API 或命令",
    "GUI 不直接编辑订阅、系统代理、DNS、TUN 或 launchd",
    "GUI 先做只读面板，再做手动 apply/rollback 按钮，最后再考虑常驻菜单栏",
]


def steady_report(run_connectivity: bool = False, run_delay: bool = False) -> dict[str, Any]:
    data = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "product": PRODUCT_IDENTITY,
        "audit": collect_audit(),
        "config_summary": summarize_config(),
        "drift": detect_drift(),
        "proxy_residue": proxy_residue_check(),
        "launchd": launchd_status(),
        "connectivity": batch_connectivity(timeout=6) if run_connectivity else {"skipped": True},
        "delay": mihomo_delay(limit=10) if run_delay else {"skipped": True},
        "risks": RISK_ITEMS,
        "usage": USAGE_LINES,
        "gui_route": GUI_ROUTE,
    }
    return data


def write_steady_report(run_connectivity: bool = False, run_delay: bool = False, reports_dir: Path = REPORTS_DIR) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    data = steady_report(run_connectivity=run_connectivity, run_delay=run_delay)
    path = reports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-steady.json"
    path.write_text(json.dumps(to_jsonable(data), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
