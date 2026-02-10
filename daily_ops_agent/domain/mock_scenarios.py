from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    description: str


SCENARIOS: list[Scenario] = [
    Scenario(
        key="steady_growth",
        title="Steady growth",
        description="Healthy upward trend, no major alerts.",
    ),
    Scenario(
        key="cr_drop",
        title="CR drop (site issue)",
        description="Sessions stable but orders drop sharply → CR alert.",
    ),
    Scenario(
        key="ad_spend_spike",
        title="Ad spend spike (efficiency down)",
        description="Spend increases but attributed revenue doesn’t → ROAS alert.",
    ),
    Scenario(
        key="revenue_crash",
        title="Revenue crash (multiple alerts)",
        description="Revenue and orders drop hard → revenue/orders/CR alerts.",
    ),
]


def list_scenarios() -> list[dict]:
    return [s.__dict__ for s in SCENARIOS]


def generate_series(scenario_key: str, days: int = 8, end_day: date | None = None) -> list[dict]:
    """Return a list of payload dicts compatible with POST /metrics.

    Produces deterministic numbers (no randomness) so the UI can reliably show different results.
    """
    if end_day is None:
        end_day = date.today()

    start = end_day - timedelta(days=days - 1)

    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        day = d.isoformat()

        # Baseline-ish numbers
        revenue = 12000 + i * 120
        orders = 140 + i
        sessions = 11000 + i * 30
        meta_spend = 800 + i * 10
        meta_revenue = 4200 + i * 25
        google_spend = 620 + i * 8
        google_revenue = 3100 + i * 20

        if scenario_key == "steady_growth":
            pass

        elif scenario_key == "cr_drop":
            # last day: orders down, sessions stable
            if i == days - 1:
                orders = int(orders * 0.65)
                revenue = int(revenue * 0.70)

        elif scenario_key == "ad_spend_spike":
            # last day: spend spikes, revenue flat
            if i == days - 1:
                meta_spend = int(meta_spend * 1.8)
                google_spend = int(google_spend * 1.6)
                meta_revenue = int(meta_revenue * 1.05)
                google_revenue = int(google_revenue * 1.02)

        elif scenario_key == "revenue_crash":
            # last day: multiple bad signals
            if i == days - 1:
                revenue = int(revenue * 0.55)
                orders = int(orders * 0.55)
                sessions = int(sessions * 0.95)
                meta_revenue = int(meta_revenue * 0.65)
                google_revenue = int(google_revenue * 0.70)

        else:
            raise ValueError(f"Unknown scenario: {scenario_key}")

        rows.append(
            {
                "day": day,
                "revenue": float(revenue),
                "orders": int(orders),
                "sessions": int(sessions),
                "meta_spend": float(meta_spend),
                "meta_revenue": float(meta_revenue),
                "google_spend": float(google_spend),
                "google_revenue": float(google_revenue),
            }
        )

    return rows
