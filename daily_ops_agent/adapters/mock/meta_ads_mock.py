from __future__ import annotations

from datetime import date


def fetch_meta_ads_metrics(day: date) -> dict:
    return {
        "spend": 820.0,
        "revenue": 4100.0,
        "ctr": 0.018,
        "cpa": 12.4,
    }
