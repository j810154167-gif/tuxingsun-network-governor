from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import BACKUPS_DIR, CLASH_VERGE_CONFIG, CLASH_VERGE_STATE
from .utils import to_jsonable


MANIFEST_NAME = "manifest.json"


def _backup_root(backups_dir: Path = BACKUPS_DIR) -> Path:
    backups_dir.mkdir(parents=True, exist_ok=True)
    path = backups_dir / datetime.now().strftime("%Y%m%d-%H%M%S")
    path.mkdir(parents=True, exist_ok=False)
    return path


def create_backup(reason: str, files: list[Path] | None = None, backups_dir: Path = BACKUPS_DIR) -> dict[str, Any]:
    selected = files or [CLASH_VERGE_CONFIG, CLASH_VERGE_STATE]
    root = _backup_root(backups_dir)
    copied = []
    for source in selected:
        entry = {"source": str(source), "exists": source.exists(), "backup": None}
        if source.exists() and source.is_file():
            target = root / source.name
            shutil.copy2(source, target)
            entry["backup"] = str(target)
        copied.append(entry)
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "reason": reason,
        "files": copied,
    }
    (root / MANIFEST_NAME).write_text(json.dumps(to_jsonable(manifest), ensure_ascii=False, indent=2), encoding="utf-8")
    return {"backup_dir": str(root), "manifest": manifest}


def latest_backup(backups_dir: Path = BACKUPS_DIR) -> Path | None:
    if not backups_dir.exists():
        return None
    candidates = [path for path in backups_dir.iterdir() if path.is_dir() and (path / MANIFEST_NAME).exists()]
    return sorted(candidates)[-1] if candidates else None


def restore_backup(backup_dir: Path | None = None) -> dict[str, Any]:
    selected = backup_dir or latest_backup()
    if selected is None:
        raise FileNotFoundError("no backup manifest found")
    manifest_path = selected / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored = []
    for item in manifest.get("files", []):
        backup = item.get("backup")
        source = item.get("source")
        entry = {"source": source, "backup": backup, "restored": False}
        if backup and source and Path(backup).exists():
            shutil.copy2(Path(backup), Path(source))
            entry["restored"] = True
        restored.append(entry)
    return {"backup_dir": str(selected), "restored": restored}
