from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from daily_ops_agent.domain.change_detection import fetch_and_hash_url
from daily_ops_agent.infra.db import db_conn


@dataclass(frozen=True)
class PageHash:
    id: int
    created_at: str
    url: str
    content_hash: str


def record_page_hash(url: str) -> PageHash:
    content_hash = fetch_and_hash_url(url)
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO page_hashes(created_at, url, content_hash) VALUES (?, ?, ?)",
            (now, url, content_hash),
        )
        conn.commit()
        new_id = int(cur.lastrowid)

    return PageHash(id=new_id, created_at=now, url=url, content_hash=content_hash)


def list_page_hashes(url: str | None = None, limit: int = 50) -> list[PageHash]:
    with db_conn() as conn:
        if url:
            cur = conn.execute(
                "SELECT id, created_at, url, content_hash FROM page_hashes WHERE url=? ORDER BY id DESC LIMIT ?",
                (url, limit),
            )
        else:
            cur = conn.execute(
                "SELECT id, created_at, url, content_hash FROM page_hashes ORDER BY id DESC LIMIT ?",
                (limit,),
            )
        rows = cur.fetchall()

    return [PageHash(id=int(r[0]), created_at=str(r[1]), url=str(r[2]), content_hash=str(r[3])) for r in rows]
