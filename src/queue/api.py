from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Dict, List, Optional

from ..config import PlaygroundConfig

_DB_LOCK = threading.Lock()


def _db_path(config: PlaygroundConfig) -> Path:
    config.ensure_directories()
    path = config.queue_db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(config: PlaygroundConfig) -> sqlite3.Connection:
    return sqlite3.connect(str(_db_path(config)))


def init_db(config: PlaygroundConfig | None = None) -> None:
    cfg = config or PlaygroundConfig.load()
    with _connect(cfg) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at REAL DEFAULT (strftime('%s','now')),
                updated_at REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _execute(query: str, params: tuple = (), *, config: PlaygroundConfig | None = None) -> None:
    cfg = config or PlaygroundConfig.load()
    with _DB_LOCK:
        with _connect(cfg) as conn:
            conn.execute(query, params)
            conn.commit()


def enqueue(item: Dict, *, config: PlaygroundConfig | None = None) -> int:
    cfg = config or PlaygroundConfig.load()
    init_db(cfg)
    with _DB_LOCK:
        with _connect(cfg) as conn:
            cursor = conn.execute(
                "INSERT INTO queue (item_json, status) VALUES (?, ?)",
                (json.dumps(item), "pending"),
            )
            conn.commit()
            return int(cursor.lastrowid)


def dequeue(*, config: PlaygroundConfig | None = None) -> Optional[Dict]:
    cfg = config or PlaygroundConfig.load()
    init_db(cfg)
    with _DB_LOCK:
        with _connect(cfg) as conn:
            paused = _is_paused(conn)
            if paused:
                return None
            row = conn.execute(
                "SELECT id, item_json FROM queue WHERE status='pending' ORDER BY id LIMIT 1"
            ).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE queue SET status='processing', updated_at=strftime('%s','now') WHERE id=?",
                (row[0],),
            )
            conn.commit()
            return {"id": row[0], "item": json.loads(row[1])}


def mark_done(item_id: int, *, config: PlaygroundConfig | None = None) -> None:
    _execute(
        "UPDATE queue SET status='done', updated_at=strftime('%s','now') WHERE id=?",
        (item_id,),
        config=config,
    )


def mark_failed(item_id: int, *, config: PlaygroundConfig | None = None) -> None:
    _execute(
        "UPDATE queue SET status='failed', updated_at=strftime('%s','now') WHERE id=?",
        (item_id,),
        config=config,
    )


def retry_item(item_id: int, *, config: PlaygroundConfig | None = None) -> None:
    _execute(
        "UPDATE queue SET status='pending', updated_at=strftime('%s','now') WHERE id=?",
        (item_id,),
        config=config,
    )


def purge_completed(*, config: PlaygroundConfig | None = None) -> None:
    _execute("DELETE FROM queue WHERE status IN ('done','failed')", config=config)


def list_items(*, status: Optional[str] = None, config: PlaygroundConfig | None = None) -> List[Dict]:
    cfg = config or PlaygroundConfig.load()
    init_db(cfg)
    with _DB_LOCK:
        with _connect(cfg) as conn:
            if status:
                rows = conn.execute(
                    "SELECT id, item_json, status, created_at, updated_at FROM queue WHERE status=? ORDER BY id",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, item_json, status, created_at, updated_at FROM queue ORDER BY id",
                ).fetchall()
    return [
        {
            "id": row[0],
            "item": json.loads(row[1]),
            "status": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }
        for row in rows
    ]


def set_paused(paused: bool, *, config: PlaygroundConfig | None = None) -> None:
    cfg = config or PlaygroundConfig.load()
    init_db(cfg)
    value = "true" if paused else "false"
    _execute(
        "INSERT INTO metadata(key,value) VALUES('paused', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (value,),
        config=cfg,
    )


def _is_paused(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT value FROM metadata WHERE key='paused'").fetchone()
    return (row and row[0] == "true") or False


def is_paused(*, config: PlaygroundConfig | None = None) -> bool:
    cfg = config or PlaygroundConfig.load()
    init_db(cfg)
    with _connect(cfg) as conn:
        return _is_paused(conn)
