from __future__ import annotations
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from chat.logger import GLOBAL_LOGGER as log

META_FILENAME = "session_meta.json"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def touch_session_meta(session_dir: Path, session_id: str) -> None:
    """Create or update per-session metadata with last_used_at timestamp."""
    session_dir.mkdir(parents=True, exist_ok=True)
    meta_path = session_dir / META_FILENAME
    now_iso = _now().isoformat()

    data: Dict[str, str] = {
        "session_id": session_id,
        "created_at": now_iso,
        "last_used_at": now_iso,
    }

    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8")) or {}
            if isinstance(existing, dict):
                data.update(existing)
        except Exception:
            pass
        data["session_id"] = session_id
        data.setdefault("created_at", now_iso)
        data["last_used_at"] = now_iso

    meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_session_meta(session_dir: Path) -> Optional[Dict[str, str]]:
    meta_path = session_dir / META_FILENAME
    if not meta_path.exists():
        return None
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def cleanup_stale_sessions(
    faiss_base: Path,
    data_base: Path,
    *,
    ttl_hours: int = 24,
    sessions: Optional[Dict[str, List[dict]]] = None,
) -> List[str]:
    """Remove sessions whose last_used_at is older than ttl_hours.

    Returns list of deleted session_ids.
    """
    deleted: List[str] = []
    cutoff = _now() - timedelta(hours=ttl_hours)

    if not faiss_base.exists():
        return deleted

    for sess_dir in faiss_base.iterdir():
        if not sess_dir.is_dir():
            continue
        meta = load_session_meta(sess_dir)
        if not meta:
            continue
        session_id = meta.get("session_id") or sess_dir.name
        last_used_raw = meta.get("last_used_at")
        last_used_dt = _parse_iso(last_used_raw) if last_used_raw else None
        if not last_used_dt or last_used_dt < cutoff:
            # Remove FAISS artifacts
            shutil.rmtree(sess_dir, ignore_errors=True)
            # Remove uploaded files
            data_dir = data_base / sess_dir.name
            if data_dir.exists():
                shutil.rmtree(data_dir, ignore_errors=True)
            if sessions is not None:
                sessions.pop(sess_dir.name, None)
            deleted.append(session_id)
            log.info(
                "Session pruned by TTL",
                session_id=session_id,
                last_used=last_used_raw,
                cutoff=cutoff.isoformat(),
            )
    return deleted
