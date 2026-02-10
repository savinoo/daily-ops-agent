from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from daily_ops_agent.infra.db import db_conn


@dataclass(frozen=True)
class MemoryItem:
    id: int
    created_at: str
    day: str | None
    decision: str
    outcome: str | None


def add_decision(decision: str, outcome: str | None = None, day: str | None = None) -> int:
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO decision_memory(created_at, day, decision, outcome) VALUES (?, ?, ?, ?)",
            (now, day, decision, outcome),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_memory(limit: int = 50) -> list[MemoryItem]:
    with db_conn() as conn:
        cur = conn.execute(
            "SELECT id, created_at, day, decision, outcome FROM decision_memory ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()

    return [
        MemoryItem(
            id=int(r[0]),
            created_at=str(r[1]),
            day=r[2],
            decision=str(r[3]),
            outcome=r[4],
        )
        for r in rows
    ]
