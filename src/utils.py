import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any, Dict
from .config import STATE_DIR, OSLO_TZ

def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def now_iso(tz: ZoneInfo = OSLO_TZ) -> str:
    return datetime.now(tz).isoformat(timespec="seconds")

def write_last_run(status: str, summary: Dict[str, int] | None = None, target_date: str | None = None) -> None:
    payload = {
        "last_run": now_iso(),
        "status": status,
        "target_date": target_date,
        "summary": summary or {}
    }
    save_json(STATE_DIR / "last_run.json", payload)
