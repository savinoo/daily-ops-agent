from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from daily_ops_agent.infra.db import db_conn


@dataclass(frozen=True)
class StoredDailyMetrics:
    day: str
    created_at: str
    revenue: float
    orders: int
    sessions: int
    meta_spend: float
    meta_revenue: float
    google_spend: float
    google_revenue: float


def upsert_metrics(m: StoredDailyMetrics) -> None:
    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO daily_metrics(day, created_at, revenue, orders, sessions, meta_spend, meta_revenue, google_spend, google_revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(day) DO UPDATE SET
              revenue=excluded.revenue,
              orders=excluded.orders,
              sessions=excluded.sessions,
              meta_spend=excluded.meta_spend,
              meta_revenue=excluded.meta_revenue,
              google_spend=excluded.google_spend,
              google_revenue=excluded.google_revenue
            """,
            (
                m.day,
                m.created_at,
                m.revenue,
                m.orders,
                m.sessions,
                m.meta_spend,
                m.meta_revenue,
                m.google_spend,
                m.google_revenue,
            ),
        )
        conn.commit()


def upsert_from_payload(day: str, payload: dict) -> None:
    created_at = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    m = StoredDailyMetrics(
        day=day,
        created_at=created_at,
        revenue=float(payload.get("revenue", 0)),
        orders=int(payload.get("orders", 0)),
        sessions=int(payload.get("sessions", 0)),
        meta_spend=float(payload.get("meta_spend", 0)),
        meta_revenue=float(payload.get("meta_revenue", 0)),
        google_spend=float(payload.get("google_spend", 0)),
        google_revenue=float(payload.get("google_revenue", 0)),
    )
    upsert_metrics(m)


def list_metrics(days: int = 30) -> list[StoredDailyMetrics]:
    with db_conn() as conn:
        cur = conn.execute(
            """
            SELECT day, created_at, revenue, orders, sessions, meta_spend, meta_revenue, google_spend, google_revenue
            FROM daily_metrics
            ORDER BY day DESC
            LIMIT ?
            """,
            (days,),
        )
        rows = cur.fetchall()

    return [
        StoredDailyMetrics(
            day=str(r[0]),
            created_at=str(r[1]),
            revenue=float(r[2]),
            orders=int(r[3]),
            sessions=int(r[4]),
            meta_spend=float(r[5]),
            meta_revenue=float(r[6]),
            google_spend=float(r[7]),
            google_revenue=float(r[8]),
        )
        for r in rows
    ]
