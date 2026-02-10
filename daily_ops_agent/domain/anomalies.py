from __future__ import annotations

from dataclasses import dataclass

from daily_ops_agent.domain.metrics import DailyMetrics


@dataclass(frozen=True)
class Alert:
    key: str
    severity: str  # low|med|high
    message: str


def compare(y: DailyMetrics, b: DailyMetrics) -> list[Alert]:
    alerts: list[Alert] = []

    def pct_change(curr: float, base: float) -> float:
        if base == 0:
            return 0.0
        return (curr - base) / base

    # Simple threshold rules (tune later)
    rev_drop = pct_change(y.revenue, b.revenue)
    if rev_drop < -0.15:
        alerts.append(Alert("revenue_drop", "high", f"Revenue down {rev_drop:.0%} vs 7d baseline"))

    cr_drop = pct_change(y.cr, b.cr)
    if cr_drop < -0.20:
        alerts.append(Alert("cr_drop", "high", f"Conversion rate down {cr_drop:.0%} vs 7d baseline"))

    meta_roas_drop = pct_change(y.meta_roas, b.meta_roas)
    if meta_roas_drop < -0.20:
        alerts.append(Alert("meta_roas_drop", "med", f"Meta ROAS down {meta_roas_drop:.0%} vs 7d baseline"))

    google_roas_drop = pct_change(y.google_roas, b.google_roas)
    if google_roas_drop < -0.20:
        alerts.append(Alert("google_roas_drop", "med", f"Google ROAS down {google_roas_drop:.0%} vs 7d baseline"))

    return alerts
