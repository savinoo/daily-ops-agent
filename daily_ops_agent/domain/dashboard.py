from __future__ import annotations

from dataclasses import asdict, dataclass

from daily_ops_agent.domain.anomalies import Alert
from daily_ops_agent.domain.metrics import DailyMetrics
from daily_ops_agent.domain.metrics_store import StoredDailyMetrics


def to_daily(m: StoredDailyMetrics) -> DailyMetrics:
    from datetime import date

    y, mm, dd = (int(x) for x in m.day.split("-"))
    return DailyMetrics(
        day=date(y, mm, dd),
        revenue=m.revenue,
        orders=m.orders,
        sessions=m.sessions,
        meta_spend=m.meta_spend,
        meta_revenue=m.meta_revenue,
        google_spend=m.google_spend,
        google_revenue=m.google_revenue,
    )


@dataclass(frozen=True)
class Baseline:
    revenue: float
    orders: float
    sessions: float
    meta_spend: float
    meta_revenue: float
    google_spend: float
    google_revenue: float


def compute_baseline(last_n: list[StoredDailyMetrics]) -> Baseline:
    if not last_n:
        return Baseline(0, 0, 0, 0, 0, 0, 0)

    def avg(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    return Baseline(
        revenue=avg([m.revenue for m in last_n]),
        orders=avg([m.orders for m in last_n]),
        sessions=avg([m.sessions for m in last_n]),
        meta_spend=avg([m.meta_spend for m in last_n]),
        meta_revenue=avg([m.meta_revenue for m in last_n]),
        google_spend=avg([m.google_spend for m in last_n]),
        google_revenue=avg([m.google_revenue for m in last_n]),
    )


def baseline_to_daily(day: str, b: Baseline) -> DailyMetrics:
    from datetime import date

    y, mm, dd = (int(x) for x in day.split("-"))
    return DailyMetrics(
        day=date(y, mm, dd),
        revenue=b.revenue,
        orders=int(round(b.orders)),
        sessions=int(round(b.sessions)),
        meta_spend=b.meta_spend,
        meta_revenue=b.meta_revenue,
        google_spend=b.google_spend,
        google_revenue=b.google_revenue,
    )


def compute_alerts(curr: StoredDailyMetrics, baseline: Baseline) -> list[Alert]:
    from daily_ops_agent.domain.anomalies import compare

    y = to_daily(curr)
    b = baseline_to_daily(curr.day, baseline)
    return compare(y, b)


def asdict_metrics(m: StoredDailyMetrics) -> dict:
    return asdict(m)


def asdict_baseline(b: Baseline) -> dict:
    return asdict(b)
