from datetime import date

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.metrics import DailyMetrics


def test_revenue_drop_alert():
    y = DailyMetrics(
        day=date(2026, 1, 2),
        revenue=80,
        orders=10,
        sessions=1000,
        meta_spend=10,
        meta_revenue=10,
        google_spend=10,
        google_revenue=10,
    )
    b = DailyMetrics(
        day=date(2026, 1, 1),
        revenue=120,
        orders=10,
        sessions=1000,
        meta_spend=10,
        meta_revenue=10,
        google_spend=10,
        google_revenue=10,
    )

    alerts = compare(y, b)
    assert any(a.key == "revenue_drop" for a in alerts)
