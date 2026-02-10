from __future__ import annotations

from daily_ops_agent.domain.anomalies import Alert
from daily_ops_agent.domain.metrics import DailyMetrics


def render_brief(y: DailyMetrics, b: DailyMetrics, alerts: list[Alert]) -> str:
    lines: list[str] = []

    lines.append(f"# Daily Ops Brief — {y.day.isoformat()}")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- Revenue: **${y.revenue:,.0f}** (baseline ${b.revenue:,.0f})")
    lines.append(f"- Orders: **{y.orders:,}** (baseline {b.orders:,})")
    lines.append(f"- AOV: **${y.aov:,.2f}** (baseline ${b.aov:,.2f})")
    lines.append(f"- CR: **{y.cr*100:.2f}%** (baseline {b.cr*100:.2f}%)")
    lines.append("")

    lines.append("## Paid Media")
    lines.append(f"- Meta spend: ${y.meta_spend:,.0f} | ROAS: {y.meta_roas:.2f} (baseline {b.meta_roas:.2f})")
    lines.append(f"- Google spend: ${y.google_spend:,.0f} | ROAS: {y.google_roas:.2f} (baseline {b.google_roas:.2f})")
    lines.append("")

    lines.append("## Alerts")
    if not alerts:
        lines.append("- No alerts triggered.")
    else:
        for a in alerts:
            lines.append(f"- [{a.severity.upper()}] {a.message}")

    lines.append("")
    lines.append("## Decision memory")
    lines.append("- See /memory endpoint (SQLite) — add decisions + outcomes to improve future briefs")

    return "\n".join(lines)
