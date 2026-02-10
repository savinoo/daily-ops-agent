from __future__ import annotations

from daily_ops_agent.domain.mock_scenarios import generate_series


def test_generate_series_has_daily_variation() -> None:
    rows = generate_series("steady_growth", days=8)
    assert len(rows) == 8

    # Revenue should not be perfectly monotonic linear due to jitter
    revs = [r["revenue"] for r in rows]
    assert len(set(revs)) == 8


def test_scenarios_diverge_on_last_day() -> None:
    base = generate_series("steady_growth", days=8)
    crash = generate_series("revenue_crash", days=8)

    assert crash[-1]["revenue"] < base[-1]["revenue"]
    assert crash[-1]["orders"] < base[-1]["orders"]
