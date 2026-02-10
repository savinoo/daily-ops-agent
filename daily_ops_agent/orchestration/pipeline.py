from __future__ import annotations

from datetime import date, timedelta

from daily_ops_agent.domain.metrics import DailyMetrics
from daily_ops_agent.infra.settings import settings


def _fetch(day: date) -> DailyMetrics:
    # For MVP: only mock adapters
    if not settings.use_mock_adapters:
        raise NotImplementedError("Real adapters not implemented yet")

    from daily_ops_agent.adapters.mock.shopify_mock import fetch_shopify_metrics
    from daily_ops_agent.adapters.mock.meta_ads_mock import fetch_meta_ads_metrics
    from daily_ops_agent.adapters.mock.google_ads_mock import fetch_google_ads_metrics

    shop = fetch_shopify_metrics(day)
    meta = fetch_meta_ads_metrics(day)
    gg = fetch_google_ads_metrics(day)

    return DailyMetrics(
        day=day,
        revenue=float(shop["revenue"]),
        orders=int(shop["orders"]),
        sessions=int(shop["sessions"]),
        meta_spend=float(meta["spend"]),
        meta_revenue=float(meta["revenue"]),
        google_spend=float(gg["spend"]),
        google_revenue=float(gg["revenue"]),
    )


def fetch_yesterday_and_baseline(today: date) -> tuple[DailyMetrics, DailyMetrics]:
    yesterday = today - timedelta(days=1)
    baseline_day = today - timedelta(days=7)
    return _fetch(yesterday), _fetch(baseline_day)
