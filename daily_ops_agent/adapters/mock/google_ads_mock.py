from __future__ import annotations

from datetime import date


def fetch_google_ads_metrics(day: date) -> dict:
    return {
        "spend": 640.0,
        "revenue": 2900.0,
        "ctr": 0.022,
        "cpa": 14.1,
    }
