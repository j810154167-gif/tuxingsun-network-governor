from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from .apply import _request_unix
from .paths import MIHOMO_SOCKET
from .utils import run_command


DIRECT_URLS = [
    "https://www.baidu.com",
    "https://www.qq.com",
    "https://www.aliyun.com",
    "https://www.eastmoney.com",
    "https://trae.ai",
]

PROXY_URLS = [
    "https://github.com",
    "https://raw.githubusercontent.com",
    "https://api.openai.com",
    "https://api.anthropic.com",
    "https://claude.ai",
    "https://api.search.brave.com",
    "https://www.gstatic.com/generate_204",
]


def curl_url(url: str, proxy: str | None = None, timeout: int = 8) -> dict[str, Any]:
    command = ["curl", "-L", "-s", "-o", "/dev/null", "-w", "%{http_code} %{time_total}", "--max-time", str(timeout)]
    if proxy:
        command.extend(["--proxy", proxy])
    command.append(url)
    result = run_command(command, timeout=timeout + 2)
    parts = result["stdout"].split()
    status = parts[0] if parts else "000"
    elapsed = parts[1] if len(parts) > 1 else None
    return {"url": url, "proxy": proxy, "status": status, "elapsed": elapsed, "ok": status != "000", "raw": result}


def batch_connectivity(proxy: str = "http://127.0.0.1:7897", timeout: int = 8) -> dict[str, Any]:
    direct_results = [curl_url(url, timeout=timeout) for url in DIRECT_URLS]
    proxy_results = [curl_url(url, proxy=proxy, timeout=timeout) for url in PROXY_URLS]
    return {
        "direct": direct_results,
        "proxy": proxy_results,
        "summary": {
            "direct_ok": sum(1 for item in direct_results if item["ok"]),
            "proxy_ok": sum(1 for item in proxy_results if item["ok"]),
            "direct_total": len(direct_results),
            "proxy_total": len(proxy_results),
        },
    }


def mihomo_delay(timeout_ms: int = 8000, url: str = "https://www.gstatic.com/generate_204", limit: int = 20) -> dict[str, Any]:
    if not MIHOMO_SOCKET.exists():
        return {"attempted": False, "ok": False, "reason": "mihomo socket missing"}
    response = _request_unix("GET", "/proxies")
    body = response.split("\r\n\r\n", 1)[-1]
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"attempted": True, "ok": False, "reason": "proxies response is not json", "response_head": response[:200]}
    proxies = data.get("proxies", {})
    names = [name for name, item in proxies.items() if isinstance(item, dict) and item.get("type") not in {"Direct", "Reject", "Selector", "URLTest", "Fallback", "LoadBalance"}]
    results = []
    for name in names[:limit]:
        encoded = urllib.parse.quote(name, safe="")
        path = f"/proxies/{encoded}/delay?timeout={timeout_ms}&url={urllib.parse.quote(url, safe='')}"
        item_response = _request_unix("GET", path, timeout=max(3, timeout_ms // 1000 + 3))
        item_body = item_response.split("\r\n\r\n", 1)[-1]
        try:
            item_data = json.loads(item_body)
        except json.JSONDecodeError:
            item_data = {"error": item_body[:120]}
        results.append({"name": name, "result": item_data})
    return {"attempted": True, "ok": True, "count": len(results), "results": results}
