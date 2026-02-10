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

    Produces deterministic numbers with *daily variation* (seeded by day+scenario) so the demo feels real,
    while still being reproducible.
    """

    import hashlib

    def jitter(day_str: str, scale: float) -> float:
        h = hashlib.sha256(f"{scenario_key}:{day_str}".encode("utf-8")).hexdigest()
        # 0..1
        x = int(h[:8], 16) / 0xFFFFFFFF
        # map to [-1, +1]
        x = (x * 2.0) - 1.0
        return x * scale

    if end_day is None:
        end_day = date.today()

    start = end_day - timedelta(days=days - 1)

    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        day = d.isoformat()

        # Baseline-ish numbers with gentle trend + deterministic daily noise
        revenue = (12000 + i * 120) * (1.0 + jitter(day, 0.04))
        orders = (140 + i) * (1.0 + jitter(day, 0.03))
        sessions = (11000 + i * 30) * (1.0 + jitter(day, 0.02))

        meta_spend = (800 + i * 10) * (1.0 + jitter(day, 0.05))
        meta_revenue = (4200 + i * 25) * (1.0 + jitter(day, 0.04))
        google_spend = (620 + i * 8) * (1.0 + jitter(day, 0.05))
        google_revenue = (3100 + i * 20) * (1.0 + jitter(day, 0.04))

        if scenario_key == "steady_growth":
            pass

        elif scenario_key == "cr_drop":
            # last day: orders down, sessions stable
            if i == days - 1:
                orders *= 0.65
                revenue *= 0.72

        elif scenario_key == "ad_spend_spike":
            # last day: spend spikes, revenue does not keep up
            if i == days - 1:
                meta_spend *= 1.8
                google_spend *= 1.6
                meta_revenue *= 1.05
                google_revenue *= 1.02

        elif scenario_key == "revenue_crash":
            # last day: multiple bad signals
            if i == days - 1:
                revenue *= 0.55
                orders *= 0.55
                sessions *= 0.95
                meta_revenue *= 0.65
                google_revenue *= 0.70

        else:
            raise ValueError(f"Unknown scenario: {scenario_key}")

        rows.append(
            {
                "day": day,
                "revenue": round(float(revenue), 2),
                "orders": int(round(float(orders))),
                "sessions": int(round(float(sessions))),
                "meta_spend": round(float(meta_spend), 2),
                "meta_revenue": round(float(meta_revenue), 2),
                "google_spend": round(float(google_spend), 2),
                "google_revenue": round(float(google_revenue), 2),
            }
        )

    return rows
